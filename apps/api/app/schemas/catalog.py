from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UnitCreate(BaseModel):
    code: str
    name: str
    dimension: str
    factor_to_base: Decimal
    is_base: bool


class UnitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    dimension: str
    factor_to_base: Decimal
    is_base: bool


class UnitUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    dimension: str | None = None
    factor_to_base: Decimal | None = None
    is_base: bool | None = None


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProductCreate(BaseModel):
    sku: str | None = None
    name: str
    description: str | None = None

    category_id: UUID | None = None
    base_unit_id: UUID

    is_sellable: bool = False
    is_purchasable: bool = False
    is_recipe_component: bool = False
    is_manufactured: bool = False

    track_inventory: bool = True
    minimum_stock: Decimal = Field(default=Decimal("0.0"), ge=0)
    target_stock: Decimal | None = Field(default=None, ge=0)
    shelf_life_days: int | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sku: str | None
    name: str
    description: str | None

    category: CategoryRead | None
    base_unit: UnitRead

    is_sellable: bool
    is_purchasable: bool
    is_recipe_component: bool
    is_manufactured: bool

    track_inventory: bool
    minimum_stock: Decimal
    target_stock: Decimal | None
    shelf_life_days: int | None

    active: bool
    activated_at: datetime | None
    desactivated_at: datetime | None

class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None

    category_id: UUID | None = None
    base_unit_id: UUID | None = None

    is_sellable: bool | None = None
    is_purchasable: bool | None = None
    is_recipe_component: bool | None = None
    is_manufactured: bool | None = None

    track_inventory: bool | None = None
    minimum_stock: Decimal | None = None
    target_stock: Decimal | None = None
    shelf_life_days: int | None = None

    active: bool | None = None
    activated_at: datetime | None = None
    deactivated_at: datetime | None = None