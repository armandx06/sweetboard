from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str | None


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: str | None
    created_at: datetime
    updated_at: datetime | None
