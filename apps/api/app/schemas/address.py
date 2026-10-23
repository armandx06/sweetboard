from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AddressCreateBody(BaseModel):
    subject_id: UUID
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
