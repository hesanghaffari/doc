import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SlotStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    CANCELLED = "cancelled"


class AppointmentSlot(Base):
    """
    A single bookable time slot created by a doctor.
    Reservation is a separate table so cancellation history is preserved
    even after a slot is freed up again.
    """

    __tablename__ = "appointment_slots"
    __table_args__ = (
        UniqueConstraint("doctor_id", "start_time", name="uq_doctor_slot_start"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(SlotStatus), nullable=False, default=SlotStatus.AVAILABLE, index=True)

    doctor = relationship("Doctor", back_populates="slots")
    reservation = relationship(
        "Reservation", back_populates="slot", uselist=False, cascade="all, delete-orphan"
    )
