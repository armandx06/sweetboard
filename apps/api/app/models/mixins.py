from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )


class NameMixin:
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()


class ContactMixin:
    phone_number: Mapped[str] = mapped_column()
    email: Mapped[str | None] = mapped_column()


class PersonMixin(UUIDMixin, NameMixin, ContactMixin, TimestampMixin):
    pass
