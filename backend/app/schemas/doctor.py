import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.user import UserRead


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    specialty: str = Field(min_length=2, max_length=150)
    bio: str | None = None
    clinic_address: str | None = None


class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    specialty: str
    bio: str | None
    clinic_address: str | None
    user: UserRead
