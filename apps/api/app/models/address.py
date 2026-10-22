from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Address(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "addresses"

    street: Mapped[str] = mapped_column()
    exterior_number: Mapped[str] = mapped_column()
    interior_number: Mapped[str | None] = mapped_column()
    neighborhood: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    postal_code: Mapped[str] = mapped_column()
    address_notes: Mapped[str | None] = mapped_column()
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8))
