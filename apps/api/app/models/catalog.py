from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.address import Address


class Unit(Base, UUIDMixin):
    __tablename__ = "units"

    code: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    dimension: Mapped[str] = mapped_column()
    factor_to_base: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    is_base: Mapped[bool] = mapped_column()

    __table_args__ = (
        CheckConstraint(
            "dimension IN ('mass', 'volume', 'count', 'time', 'temperature', 'length')",
            "dimension_valid",
        ),
        CheckConstraint("factor_to_base > 0", "factor_positive"),
        CheckConstraint("NOT is_base OR factor_to_base = 1", "base_factor_is_one"),
        Index(
            "uq_units_one_base_per_dimension",
            "dimension",
            unique=True,
            postgresql_where=text("is_base = true"),
        ),
    )


class Category(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column()


class Location(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(unique=True)
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("addresses.id", ondelete="RESTRICT"), index=True
    )
    is_default: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=False)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()

    address: Mapped["Address"] = relationship(back_populates="locations")

    __table_args__ = (
        Index(
            "uq_locations_one_default",
            "is_default",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )


class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()

    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )
    base_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("units.id", ondelete="RESTRICT"), index=True
    )

    is_sellable: Mapped[bool] = mapped_column(default=False)
    is_purchasable: Mapped[bool] = mapped_column(default=False)
    is_recipe_component: Mapped[bool] = mapped_column(default=False)
    is_manufactured: Mapped[bool] = mapped_column(default=False)

    track_inventory: Mapped[bool] = mapped_column(default=True)
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=0)
    target_stock: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    shelf_life_days: Mapped[int | None] = mapped_column()

    active: Mapped[bool] = mapped_column(default=False)
    activated_at: Mapped[date | None] = mapped_column()
    deactivated_at: Mapped[date | None] = mapped_column()

    category: Mapped["Category | None"] = relationship()
    base_unit: Mapped["Unit"] = relationship()

    __table_args__ = (
        CheckConstraint("minimum_stock >= 0", "minimum_stock_non_negative"),
        CheckConstraint(
            "target_stock is null or target_stock >= minimum_stock",
            "target_stock_null_or_greater_than_minimum",
        ),
        CheckConstraint(
            "shelf_life_days is null or shelf_life_days >= 0", "shelf_life_non_negative"
        ),
        CheckConstraint(
            "is_sellable OR is_purchasable OR is_recipe_component OR is_manufactured",
            "at_least_one_capability",
        ),
        CheckConstraint(
            "track_inventory OR (minimum_stock = 0 AND target_stock IS NULL)",
            "non_inventory_no_stock_targets",
        ),
    )
