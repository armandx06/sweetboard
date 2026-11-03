from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime import today
from app.exceptions.exceptions import (
    ActiveCustomer,
    CustomerAddressNotFound,
    CustomerNotFound,
    InactiveCustomer,
)
from app.models.address import Address, CustomerAddress
from app.models.customer import Customer
from app.schemas.address import (
    AddressCreateBody,
    AddressRead,
    CustomerSupplierAddressRead,
    CustomerSupplierAddressUpdateBody,
)
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate


def _address_to_read(link: CustomerAddress) -> CustomerSupplierAddressRead:
    return CustomerSupplierAddressRead(
        **AddressRead.model_validate(link.address).model_dump(),
        is_default=link.is_default,
        is_billing=link.is_billing,
        active=link.active,
        activated_at=link.activated_at,
        deactivated_at=link.deactivated_at,
    )


def _customer_to_read(customer: Customer) -> CustomerRead:
    return CustomerRead(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone_number=customer.phone_number,
        email=customer.email,
        addresses=[_address_to_read(link) for link in customer.addresses],
        company_name=customer.company_name,
        is_company=customer.is_company,
        active=customer.active,
        activated_at=customer.activated_at,
        deactivated_at=customer.deactivated_at,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


async def create_customer(db: AsyncSession, data: CustomerCreate) -> CustomerRead:
    data.first_name = data.first_name.strip().title()
    data.last_name = data.last_name.strip().title()
    data.phone_number = data.phone_number.strip()
    data.email = data.email.strip().lower() if data.email else None
    data.company_name = data.company_name.strip() if data.company_name else None

    customer = Customer(
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        email=data.email,
        company_name=data.company_name,
        is_company=data.is_company,
    )
    db.add(customer)

    await db.commit()

    return await get_customer(db, customer.id)


async def create_customer_address(
    db: AsyncSession,
    customer_id: UUID,
    address_data: AddressCreateBody,
    is_default: bool = False,
    is_billing: bool = False,
) -> CustomerSupplierAddressRead:
    if not await customer_exists(db, customer_id):
        raise CustomerNotFound

    address = Address(**address_data.model_dump())
    db.add(address)
    await db.flush()

    if is_default:
        await _clear_default_address(db, customer_id, address.id)

    customer_address = CustomerAddress(
        customer_id=customer_id,
        address=address,
        is_default=is_default,
        is_billing=is_billing,
        active=True,
        activated_at=today(),
    )
    db.add(customer_address)

    await db.commit()
    await db.refresh(address)

    return _address_to_read(customer_address)


async def customer_exists(db: AsyncSession, customer_id: UUID) -> bool:
    stmt = select(Customer.id).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    return customer is not None


async def _get_customer_orm(db: AsyncSession, customer_id: UUID) -> Customer:
    stmt = (
        select(Customer)
        .options(selectinload(Customer.addresses).selectinload(CustomerAddress.address))
        .where(Customer.id == customer_id)
        .execution_options(populate_existing=True)
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise CustomerNotFound

    return customer


async def get_customer(db: AsyncSession, customer_id: UUID) -> CustomerRead:
    return _customer_to_read(await _get_customer_orm(db, customer_id))


async def list_customers(
    db: AsyncSession, include_inactive: bool = False
) -> list[CustomerRead]:
    stmt = select(Customer).options(
        selectinload(Customer.addresses).selectinload(CustomerAddress.address)
    )
    if not include_inactive:
        stmt = stmt.where(Customer.active.is_(True))
    result = await db.execute(stmt)

    return [_customer_to_read(customer) for customer in result.scalars().all()]


async def list_customer_addresses(
    db: AsyncSession, customer_id: UUID
) -> list[CustomerSupplierAddressRead]:
    if not await customer_exists(db, customer_id):
        raise CustomerNotFound

    stmt = (
        select(CustomerAddress)
        .options(selectinload(CustomerAddress.address))
        .where(CustomerAddress.customer_id == customer_id)
    )
    result = await db.execute(stmt)

    return [_address_to_read(link) for link in result.scalars().all()]


async def _get_customer_address(
    db: AsyncSession, customer_id: UUID, address_id: UUID
) -> CustomerAddress:
    stmt = (
        select(CustomerAddress)
        .options(selectinload(CustomerAddress.address))
        .where(
            CustomerAddress.customer_id == customer_id,
            CustomerAddress.address_id == address_id,
        )
    )
    link = (await db.execute(stmt)).scalar_one_or_none()

    if link is None:
        raise CustomerAddressNotFound

    return link


async def _get_default_customer_address(
    db: AsyncSession, customer_id: UUID
) -> CustomerAddress | None:
    stmt = select(CustomerAddress).where(
        CustomerAddress.customer_id == customer_id,
        CustomerAddress.is_default.is_(True),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _clear_default_address(
    db: AsyncSession, customer_id: UUID, address_id: UUID
) -> None:
    current_default = await _get_default_customer_address(db, customer_id)
    if current_default is not None and current_default.address_id != address_id:
        current_default.is_default = False
        await db.flush()


async def update_customer_address(
    db: AsyncSession,
    customer_id: UUID,
    address_id: UUID,
    data: CustomerSupplierAddressUpdateBody,
) -> CustomerSupplierAddressRead:
    customer_address = await _get_customer_address(db, customer_id, address_id)
    address = customer_address.address

    update_data = data.model_dump(exclude_unset=True)
    is_default = update_data.pop("is_default", None)
    is_billing = update_data.pop("is_billing", None)

    for field, value in update_data.items():
        setattr(address, field, value)

    if is_default is True:
        await _clear_default_address(db, customer_id, address_id)
        customer_address.is_default = True
    elif is_default is False:
        customer_address.is_default = False

    if is_billing is not None:
        customer_address.is_billing = is_billing

    await db.commit()
    await db.refresh(address)

    return _address_to_read(customer_address)


async def delete_customer_address(
    db: AsyncSession, customer_id: UUID, address_id: UUID
) -> None:
    customer_address = await _get_customer_address(db, customer_id, address_id)

    customer_address.is_default = False
    customer_address.is_billing = False
    customer_address.active = False
    customer_address.deactivated_at = today()

    await db.commit()


async def update_customer(
    db: AsyncSession, customer_id: UUID, data: CustomerUpdate
) -> CustomerRead:
    customer = await _get_customer_orm(db, customer_id)

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
        setattr(customer, field, value)

    await db.commit()

    return await get_customer(db, customer.id)


async def activate_customer(
    db: AsyncSession, customer_id: UUID, activated_at: date | None = None
) -> CustomerRead:
    customer = await _get_customer_orm(db, customer_id)

    if customer.active:
        raise ActiveCustomer

    customer.active = True
    customer.activated_at = activated_at or today()
    customer.deactivated_at = None

    await db.commit()

    return await get_customer(db, customer.id)


async def deactivate_customer(
    db: AsyncSession, customer_id: UUID, deactivated_at: date | None = None
) -> CustomerRead:
    customer = await _get_customer_orm(db, customer_id)

    if not customer.active:
        raise InactiveCustomer

    customer.active = False
    customer.deactivated_at = deactivated_at or today()

    await db.commit()

    return await get_customer(db, customer.id)


async def delete_customer(db: AsyncSession, customer_id: UUID) -> None:
    customer = await _get_customer_orm(db, customer_id)

    await db.delete(customer)
    await db.commit()
