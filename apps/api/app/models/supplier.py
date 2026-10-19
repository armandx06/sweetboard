from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import PersonMixin


class Supplier(Base, PersonMixin):
    __tablename__ = "suppliers"

    rfc: Mapped[str | None] = mapped_column()
    company_name: Mapped[str | None] = mapped_column()
    is_company: Mapped[bool] = mapped_column(default=False)
    provide_invoice: Mapped[bool] = mapped_column(default=False)
    lead_time_days: Mapped[int] = mapped_column(default=0)
    minimum_order_quantity: Mapped[int] = mapped_column(default=1)
    minimum_order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    active: Mapped[bool] = mapped_column(default=False)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()

    __table_args__ = (
        CheckConstraint("length(rfc) >= 12 and length(rfc) <= 13", "rfc_length"),
        CheckConstraint("lead_time_days >= 0", "lead_time_days_non_negative"),
        CheckConstraint("minimum_order_quantity >= 1", "min_order_qty_positive"),
        CheckConstraint("minimum_order_value >= 0", "min_order_value_non_negative"),
    )
