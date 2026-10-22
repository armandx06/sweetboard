from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

RFC_PATTERN = r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"


def _normalize_rfc(value: object) -> object:
    return value.strip().upper() if isinstance(value, str) else value


class SupplierCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str | None = None
    rfc: str | None = Field(default=None, pattern=RFC_PATTERN)
    company_name: str | None = None
    is_company: bool = False
    provide_invoice: bool = False
    lead_time_days: int = Field(default=0, ge=0)
    minimum_order_value: Decimal = Field(default=Decimal("0.0"), ge=0)

    @field_validator("rfc", mode="before")
    @classmethod
    def normalize_rfc(cls, value: object) -> object:
        return _normalize_rfc(value)


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: str | None
    rfc: str | None
    company_name: str | None
    is_company: bool
    provide_invoice: bool
    lead_time_days: int
    minimum_order_value: Decimal
    active: bool
    activated_at: date | None
    deactivated_at: date | None
    created_at: datetime
    updated_at: datetime | None


class SupplierUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    rfc: str | None = Field(default=None, pattern=RFC_PATTERN)
    company_name: str | None = None
    is_company: bool | None = None
    provide_invoice: bool | None = None
    lead_time_days: int | None = Field(default=None, ge=0)
    minimum_order_value: Decimal | None = Field(default=None, ge=0)

    @field_validator("rfc", mode="before")
    @classmethod
    def normalize_rfc(cls, value: object) -> object:
        return _normalize_rfc(value)
