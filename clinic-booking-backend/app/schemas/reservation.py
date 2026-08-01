import uuid

from pydantic import BaseModel, ConfigDict

from app.models.reservation import ReservationStatus
from app.schemas.appointment import SlotRead


class ReservationCreate(BaseModel):
    slot_id: uuid.UUID
    reason: str | None = None


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ReservationStatus
    reason: str | None
    slot: SlotRead
