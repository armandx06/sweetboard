from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import PersonMixin

if TYPE_CHECKING:
    from app.models.address import CustomerAddress


class Customer(Base, PersonMixin):
    __tablename__ = "customers"

    company_name: Mapped[str | None] = mapped_column()
    is_company: Mapped[bool] = mapped_column(default=False)
    addresses: Mapped[list["CustomerAddress"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    active: Mapped[bool] = mapped_column(default=False)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()
