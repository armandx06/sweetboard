from datetime import date, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import (
    PersonMixin,
)


class Employee(Base, PersonMixin):
    __tablename__ = "employees"

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    birth_date: Mapped[date] = mapped_column()
    hire_date: Mapped[date | None] = mapped_column()
    termination_date: Mapped[date | None] = mapped_column()
    active: Mapped[bool] = mapped_column(default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_password_change_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
