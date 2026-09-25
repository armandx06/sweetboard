from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseEmployee(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    phone_number: str


class EmployeeCreate(BaseEmployee):
    email: str | None = None


class EmployeeRead(BaseEmployee):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str | None
    hire_date: date | None
    termination_date: date | None
    active: bool
    last_login_at: datetime | None
    last_password_change_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


class EmployeeCreateResponse(EmployeeRead):
    temporary_password: str


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: str | None = None


class PasswordResetResponse(BaseModel):
    temporary_password: str
