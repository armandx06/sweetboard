from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Numeric, text
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
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("addresses.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    is_default: Mapped[bool] = mapped_column(default=False)
    is_billing: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        Index(
            "uq_customer_addresses_one_default",
            "customer_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )


class EmployeeAddress(Base):
    __tablename__ = "employee_addresses"

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("addresses.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    is_default: Mapped[bool] = mapped_column(default=False)
    is_billing: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        Index(
            "uq_employee_addresses_one_default",
            "employee_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )


class SupplierAddress(Base):
    __tablename__ = "supplier_addresses"

    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), primary_key=True
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("addresses.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    is_default: Mapped[bool] = mapped_column(default=False)
    is_billing: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        Index(
            "uq_supplier_addresses_one_default",
            "supplier_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )
