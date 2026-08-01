import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    specialty = Column(String(150), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    clinic_address = Column(String(255), nullable=True)

    user = relationship("User", back_populates="doctor_profile")
    slots = relationship(
        "AppointmentSlot", back_populates="doctor", cascade="all, delete-orphan"
    )
