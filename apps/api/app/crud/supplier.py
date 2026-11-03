from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime import today
from app.exceptions.exceptions import (
    ActiveSupplier,
    InactiveSupplier,
    SupplierAddressNotFound,
    SupplierNotFound,
)
from app.models.address import Address, SupplierAddress
from app.models.supplier import Supplier
from app.schemas.address import (
    AddressCreateBody,
    AddressRead,
    CustomerSupplierAddressRead,
    CustomerSupplierAddressUpdateBody,
)
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate


def _address_to_read(link: SupplierAddress) -> CustomerSupplierAddressRead:
    return CustomerSupplierAddressRead(
        **AddressRead.model_validate(link.address).model_dump(),
        is_default=link.is_default,
        is_billing=link.is_billing,
        active=link.active,
        activated_at=link.activated_at,
        deactivated_at=link.deactivated_at,
    )


def _supplier_to_read(supplier: Supplier) -> SupplierRead:
    return SupplierRead(
        id=supplier.id,
        first_name=supplier.first_name,
        last_name=supplier.last_name,
        phone_number=supplier.phone_number,
        email=supplier.email,
        addresses=[_address_to_read(link) for link in supplier.addresses],
        rfc=supplier.rfc,
        company_name=supplier.company_name,
        is_company=supplier.is_company,
        provide_invoice=supplier.provide_invoice,
        lead_time_days=supplier.lead_time_days,
        minimum_order_value=supplier.minimum_order_value,
        active=supplier.active,
        activated_at=supplier.activated_at,
        deactivated_at=supplier.deactivated_at,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
    )


async def create_supplier(db: AsyncSession, data: SupplierCreate) -> SupplierRead:
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

    return await get_supplier(db, supplier.id)


async def create_supplier_address(
    db: AsyncSession,
    supplier_id: UUID,
    address_data: AddressCreateBody,
    is_default: bool = False,
    is_billing: bool = False,
) -> CustomerSupplierAddressRead:
    if not await supplier_exists(db, supplier_id):
        raise SupplierNotFound

    address = Address(**address_data.model_dump())
    db.add(address)
    await db.flush()

    if is_default:
        await _clear_default_address(db, supplier_id, address.id)

    supplier_address = SupplierAddress(
        supplier_id=supplier_id,
        address=address,
        is_default=is_default,
        is_billing=is_billing,
        active=True,
        activated_at=today(),
    )
    db.add(supplier_address)

    await db.commit()
    await db.refresh(address)

    return _address_to_read(supplier_address)


async def supplier_exists(db: AsyncSession, supplier_id: UUID) -> bool:
    stmt = select(Supplier.id).where(Supplier.id == supplier_id)
    result = await db.execute(stmt)
    supplier = result.scalar_one_or_none()
    return supplier is not None


async def _get_supplier_orm(db: AsyncSession, supplier_id: UUID) -> Supplier:
    stmt = (
        select(Supplier)
        .options(selectinload(Supplier.addresses).selectinload(SupplierAddress.address))
        .where(Supplier.id == supplier_id)
        .execution_options(populate_existing=True)
    )
    result = await db.execute(stmt)
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise SupplierNotFound

    return supplier


async def get_supplier(db: AsyncSession, supplier_id: UUID) -> SupplierRead:
    return _supplier_to_read(await _get_supplier_orm(db, supplier_id))


async def list_suppliers(
    db: AsyncSession, include_inactive: bool = False
) -> list[SupplierRead]:
    stmt = select(Supplier).options(
        selectinload(Supplier.addresses).selectinload(SupplierAddress.address)
    )
    if not include_inactive:
        stmt = stmt.where(Supplier.active.is_(True))
    result = await db.execute(stmt)

    return [_supplier_to_read(supplier) for supplier in result.scalars().all()]


async def list_supplier_addresses(
    db: AsyncSession, supplier_id: UUID
) -> list[CustomerSupplierAddressRead]:
    if not await supplier_exists(db, supplier_id):
        raise SupplierNotFound

    stmt = (
        select(SupplierAddress)
        .options(selectinload(SupplierAddress.address))
        .where(SupplierAddress.supplier_id == supplier_id)
    )
    result = await db.execute(stmt)

    return [_address_to_read(link) for link in result.scalars().all()]


async def _get_supplier_address(
    db: AsyncSession, supplier_id: UUID, address_id: UUID
) -> SupplierAddress:
    stmt = (
        select(SupplierAddress)
        .options(selectinload(SupplierAddress.address))
        .where(
            SupplierAddress.supplier_id == supplier_id,
            SupplierAddress.address_id == address_id,
        )
    )
    link = (await db.execute(stmt)).scalar_one_or_none()

    if link is None:
        raise SupplierAddressNotFound

    return link


async def _get_default_supplier_address(
    db: AsyncSession, supplier_id: UUID
) -> SupplierAddress | None:
    stmt = select(SupplierAddress).where(
        SupplierAddress.supplier_id == supplier_id,
        SupplierAddress.is_default.is_(True),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _clear_default_address(
    db: AsyncSession, supplier_id: UUID, address_id: UUID
) -> None:
    current_default = await _get_default_supplier_address(db, supplier_id)
    if current_default is not None and current_default.address_id != address_id:
        current_default.is_default = False
        await db.flush()


async def update_supplier_address(
    db: AsyncSession,
    supplier_id: UUID,
    address_id: UUID,
    data: CustomerSupplierAddressUpdateBody,
) -> CustomerSupplierAddressRead:
    supplier_address = await _get_supplier_address(db, supplier_id, address_id)
    address = supplier_address.address

    update_data = data.model_dump(exclude_unset=True)
    is_default = update_data.pop("is_default", None)
    is_billing = update_data.pop("is_billing", None)

    for field, value in update_data.items():
        setattr(address, field, value)

    if is_default is True:
        await _clear_default_address(db, supplier_id, address_id)
        supplier_address.is_default = True
    elif is_default is False:
        supplier_address.is_default = False

    if is_billing is not None:
        supplier_address.is_billing = is_billing

    await db.commit()
    await db.refresh(address)

    return _address_to_read(supplier_address)


async def delete_supplier_address(
    db: AsyncSession, supplier_id: UUID, address_id: UUID
) -> None:
    supplier_address = await _get_supplier_address(db, supplier_id, address_id)

    supplier_address.is_default = False
    supplier_address.is_billing = False
    supplier_address.active = False
    supplier_address.deactivated_at = today()

    await db.commit()


async def update_supplier(
    db: AsyncSession, supplier_id: UUID, data: SupplierUpdate
) -> SupplierRead:
    supplier = await _get_supplier_orm(db, supplier_id)

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

    return await get_supplier(db, supplier.id)


async def activate_supplier(
    db: AsyncSession, supplier_id: UUID, activated_at: date | None = None
) -> SupplierRead:
    supplier = await _get_supplier_orm(db, supplier_id)

    if supplier.active:
        raise ActiveSupplier

    supplier.active = True
    supplier.activated_at = activated_at or today()
    supplier.deactivated_at = None

    await db.commit()

    return await get_supplier(db, supplier.id)


async def deactivate_supplier(
    db: AsyncSession, supplier_id: UUID, deactivated_at: date | None = None
) -> SupplierRead:
    supplier = await _get_supplier_orm(db, supplier_id)

    if not supplier.active:
        raise InactiveSupplier

    supplier.active = False
    supplier.deactivated_at = deactivated_at or today()

    await db.commit()

    return await get_supplier(db, supplier.id)


async def delete_supplier(db: AsyncSession, supplier_id: UUID) -> None:
    supplier = await _get_supplier_orm(db, supplier_id)

    await db.delete(supplier)
    await db.commit()
