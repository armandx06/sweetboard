from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime import today
from app.exceptions.exceptions import (
    ActiveSupplier,
    InactiveSupplier,
    SupplierNotFound,
)
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


async def create_supplier(db: AsyncSession, data: SupplierCreate) -> Supplier:
    data.first_name = data.first_name.strip().title()
    data.last_name = data.last_name.strip().title()
    data.phone_number = data.phone_number.strip()
    data.email = data.email.strip().lower() if data.email else None
    data.company_name = data.company_name.strip() if data.company_name else None

    supplier = Supplier(
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        email=data.email,
        rfc=data.rfc,
        company_name=data.company_name,
        is_company=data.is_company,
        provide_invoice=data.provide_invoice,
        lead_time_days=data.lead_time_days,
        minimum_order_value=data.minimum_order_value,
    )
    db.add(supplier)

    await db.commit()
    await db.refresh(supplier)

    return supplier


async def get_supplier(db: AsyncSession, supplier_id: UUID) -> Supplier:
    stmt = select(Supplier).where(Supplier.id == supplier_id)
    result = await db.execute(stmt)
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise SupplierNotFound

    return supplier


async def list_suppliers(
    db: AsyncSession, include_inactive: bool = False
) -> list[Supplier]:
    stmt = select(Supplier)
    if not include_inactive:
        stmt = stmt.where(Supplier.active.is_(True))
    result = await db.execute(stmt)

    return list(result.scalars().all())


async def update_supplier(
    db: AsyncSession, supplier_id: UUID, data: SupplierUpdate
) -> Supplier:
    supplier = await get_supplier(db, supplier_id)

    update_data = data.model_dump(exclude_unset=True)

    if "first_name" in update_data:
        update_data["first_name"] = update_data["first_name"].strip().title()
    if "last_name" in update_data:
        update_data["last_name"] = update_data["last_name"].strip().title()
    if "phone_number" in update_data:
        update_data["phone_number"] = update_data["phone_number"].strip()
    if "email" in update_data:
        email = update_data["email"]
        update_data["email"] = email.strip().lower() if email else None
    if "company_name" in update_data:
        update_data["company_name"] = (
            update_data["company_name"].strip() if update_data["company_name"] else None
        )

    for field, value in update_data.items():
        setattr(supplier, field, value)

    await db.commit()
    await db.refresh(supplier)

    return supplier


async def activate_supplier(
    db: AsyncSession, supplier_id: UUID, activated_at: date | None = None
) -> Supplier:
    supplier = await get_supplier(db, supplier_id)

    if supplier.active:
        raise ActiveSupplier

    supplier.active = True
    supplier.activated_at = activated_at or today()
    supplier.deactivated_at = None

    await db.commit()
    await db.refresh(supplier)

    return supplier


async def deactivate_supplier(
    db: AsyncSession, supplier_id: UUID, deactivated_at: date | None = None
) -> Supplier:
    supplier = await get_supplier(db, supplier_id)

    if not supplier.active:
        raise InactiveSupplier

    supplier.active = False
    supplier.deactivated_at = deactivated_at or today()

    await db.commit()
    await db.refresh(supplier)

    return supplier


async def delete_supplier(db: AsyncSession, supplier_id: UUID) -> None:
    supplier = await get_supplier(db, supplier_id)

    await db.delete(supplier)
    await db.commit()
