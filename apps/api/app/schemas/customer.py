from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str | None = None
    company_name: str | None = None
    is_company: bool = False


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: str | None
    company_name: str | None
    is_company: bool = False
    active: bool = False
    activated_at: date | None
    deactivated_at: date | None
    created_at: datetime
    updated_at: datetime | None


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    company_name: str | None = None
    is_company: bool | None = None
