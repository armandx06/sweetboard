from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.catalog import Location
    from app.models.customer import Customer
    from app.models.employee import Employee
    from app.models.supplier import Supplier


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

    customer_addresses: Mapped[list["CustomerAddress"]] = relationship(
        back_populates="address"
    )
    employee_addresses: Mapped[list["EmployeeAddress"]] = relationship(
        back_populates="address"
    )
    supplier_addresses: Mapped[list["SupplierAddress"]] = relationship(
        back_populates="address"
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="address"
    )


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
    active: Mapped[bool] = mapped_column(default=True)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()

    customer: Mapped["Customer"] = relationship(back_populates="addresses")
    address: Mapped["Address"] = relationship(back_populates="customer_addresses")

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
    active: Mapped[bool] = mapped_column(default=True)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()

    employee: Mapped["Employee"] = relationship(back_populates="addresses")
    address: Mapped["Address"] = relationship(back_populates="employee_addresses")

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
    active: Mapped[bool] = mapped_column(default=True)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()

    supplier: Mapped["Supplier"] = relationship(back_populates="addresses")
    address: Mapped["Address"] = relationship(back_populates="supplier_addresses")

    __table_args__ = (
        Index(
            "uq_supplier_addresses_one_default",
            "supplier_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )
