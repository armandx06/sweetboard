from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime import today
from app.exceptions.exceptions import (
    ActiveCustomer,
    CustomerNotFound,
    InactiveCustomer,
)
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def create_customer(db: AsyncSession, data: CustomerCreate) -> Customer:
    data.first_name = data.first_name.strip().title()
    data.last_name = data.last_name.strip().title()
    data.phone_number = data.phone_number.strip()
    data.email = data.email.strip().lower() if data.email else None
    data.company_name = data.company_name.strip().title() if data.company_name else None

    customer = Customer(
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        email=data.email,
        company_name=data.company_name,
        is_company=data.is_company,
        active=data.active,
        activated_at=data.activated_at,
        deactivated_at=data.deactivated_at,
    )
    db.add(customer)

    await db.commit()
    await db.refresh(customer)

    return customer


async def get_customer(db: AsyncSession, customer_id: UUID) -> Customer:
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise CustomerNotFound

    return customer


async def list_customers(
    db: AsyncSession, include_inactive: bool = False
) -> list[Customer]:
    stmt = select(Customer)
    if not include_inactive:
        stmt = stmt.where(Customer.active.is_(True))
    result = await db.execute(stmt)

    return list(result.scalars().all())


async def update_customer(
    db: AsyncSession, customer_id: UUID, data: CustomerUpdate
) -> Customer:
    customer = await get_customer(db, customer_id)

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
            update_data["company_name"].strip().title()
            if update_data["company_name"]
            else None
        )

    for field, value in update_data.items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)

    return customer


async def activate_customer(
    db: AsyncSession, customer_id: UUID, activated_at: date | None = None
) -> Customer:
    customer = await get_customer(db, customer_id)

    if customer.active:
        raise ActiveCustomer

    customer.active = True
    customer.activated_at = activated_at or today()
    customer.deactivated_at = None

    await db.commit()
    await db.refresh(customer)

    return customer


async def deactivate_customer(
    db: AsyncSession, customer_id: UUID, deactivated_at: date | None = None
) -> Customer:
    customer = await get_customer(db, customer_id)

    if not customer.active:
        raise InactiveCustomer

    customer.active = False
    customer.deactivated_at = deactivated_at or today()

    await db.commit()
    await db.refresh(customer)

    return customer


async def delete_customer(db: AsyncSession, customer_id: UUID) -> None:
    customer = await get_customer(db, customer_id)

    await db.delete(customer)
    await db.commit()
