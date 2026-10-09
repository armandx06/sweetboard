from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import PersonMixin


class Customer(Base, PersonMixin):
    __tablename__ = "customers"

    company_name: Mapped[str | None] = mapped_column()
    is_company: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=False)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()
