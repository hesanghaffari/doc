import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.appointment import AppointmentSlot, SlotStatus
from app.models.reservation import Reservation, ReservationStatus
from app.schemas.reservation import ReservationCreate, ReservationRead

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def book_slot(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PATIENT)),
):
    """
    Patient books an available slot.
    Uses a row lock (SELECT ... FOR UPDATE) so two patients can't book the
    same slot at the same time — critical under concurrent load.
    """
    slot = (
        db.query(AppointmentSlot)
        .filter(AppointmentSlot.id == payload.slot_id)
        .with_for_update()
        .first()
    )
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")
    if slot.status != SlotStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is no longer available")

    slot.status = SlotStatus.BOOKED
    reservation = Reservation(
        slot_id=slot.id,
        patient_id=current_user.id,
        reason=payload.reason,
        status=ReservationStatus.CONFIRMED,
    )
    db.add(reservation)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is no longer available")

    db.refresh(reservation)
    return reservation


@router.get("/me", response_model=list[ReservationRead])
def my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Reservation)
        .options(joinedload(Reservation.slot))
        .filter(Reservation.patient_id == current_user.id)
        .order_by(Reservation.created_at.desc())
        .all()
    )


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    reservation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    is_owner = reservation.patient_id == current_user.id
    if not is_owner and current_user.role not in (UserRole.ADMIN, UserRole.DOCTOR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to cancel this reservation")

    reservation.status = ReservationStatus.CANCELLED
    slot = db.get(AppointmentSlot, reservation.slot_id)
    if slot:
        slot.status = SlotStatus.AVAILABLE
    db.commit()
    return None
