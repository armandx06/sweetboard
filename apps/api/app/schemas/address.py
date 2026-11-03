from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AddressCreateBody(BaseModel):
    street: str
    exterior_number: str
    interior_number: str | None = None
    neighborhood: str
    city: str
    state: str
    country: str
    postal_code: str
    address_notes: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    street: str
    exterior_number: str
    interior_number: str | None = None
    neighborhood: str
    city: str
    state: str
    country: str
    postal_code: str
    address_notes: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    created_at: datetime
    updated_at: datetime | None = None


class CustomerSupplierAddressRead(AddressRead):
    is_default: bool
    is_billing: bool
    active: bool
    activated_at: date | None = None
    deactivated_at: date | None = None


class EmployeeAddressRead(AddressRead):
    is_default: bool
    active: bool
    activated_at: date | None = None
    deactivated_at: date | None = None


class AddressUpdateBody(BaseModel):
    street: str | None = None
    exterior_number: str | None = None
    interior_number: str | None = None
    neighborhood: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    address_notes: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class CustomerSupplierAddressUpdateBody(AddressUpdateBody):
    is_default: bool | None = None
    is_billing: bool | None = None
