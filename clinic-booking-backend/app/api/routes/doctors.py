import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import hash_password
from app.api.deps import require_role
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.appointment import AppointmentSlot, SlotStatus
from app.schemas.doctor import DoctorCreate, DoctorRead
from app.schemas.appointment import SlotCreate, SlotRead

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post(
    "",
    response_model=DoctorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    """Admin-only: onboard a new doctor account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.DOCTOR,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    doctor = Doctor(
        user_id=user.id,
        specialty=payload.specialty,
        bio=payload.bio,
        clinic_address=payload.clinic_address,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("", response_model=list[DoctorRead])
def list_doctors(specialty: str | None = None, db: Session = Depends(get_db)):
    """Public: browse doctors, optionally filtered by specialty."""
    query = db.query(Doctor).options(joinedload(Doctor.user))
    if specialty:
        query = query.filter(Doctor.specialty.ilike(f"%{specialty}%"))
    return query.all()


@router.get("/me", response_model=DoctorRead)
def get_my_doctor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    """The logged-in doctor's own profile — used by the frontend dashboard."""
    doctor = (
        db.query(Doctor)
        .options(joinedload(Doctor.user))
        .filter(Doctor.user_id == current_user.id)
        .first()
    )
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return doctor


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor(doctor_id: uuid.UUID, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).options(joinedload(Doctor.user)).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor


@router.post("/{doctor_id}/slots", response_model=SlotRead, status_code=status.HTTP_201_CREATED)
def create_slot(
    doctor_id: uuid.UUID,
    payload: SlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    """A doctor opens up a new bookable time slot for themselves."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if current_user.role == UserRole.DOCTOR and doctor.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your schedule to manage")

    slot = AppointmentSlot(
        doctor_id=doctor.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=SlotStatus.AVAILABLE,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/{doctor_id}/slots", response_model=list[SlotRead])
def list_doctor_slots(
    doctor_id: uuid.UUID,
    only_available: bool = True,
    db: Session = Depends(get_db),
):
    """Public: see a doctor's open slots (patients use this to pick a time)."""
    query = db.query(AppointmentSlot).filter(AppointmentSlot.doctor_id == doctor_id)
    if only_available:
        query = query.filter(AppointmentSlot.status == SlotStatus.AVAILABLE)
    return query.order_by(AppointmentSlot.start_time).all()
