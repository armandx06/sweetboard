from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime import now, today
from app.core.security import generate_password, hash_password
from app.exceptions.exceptions import (
    ActiveEmployee,
    EmployeeAddressNotFound,
    EmployeeNotFound,
    InactiveEmployee,
)
from app.models.address import Address, EmployeeAddress
from app.models.employee import Employee
from app.schemas.address import (
    AddressCreateBody,
    AddressRead,
    EmployeeAddressRead,
    EmployeeAddressUpdateBody,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeCreateResponse,
    EmployeeRead,
    EmployeeUpdate,
)


def _address_to_read(link: EmployeeAddress) -> EmployeeAddressRead:
    return EmployeeAddressRead(
        **AddressRead.model_validate(link.address).model_dump(),
        is_default=link.is_default,
        active=link.active,
        activated_at=link.activated_at,
        deactivated_at=link.deactivated_at,
    )


def _employee_to_read(employee: Employee) -> EmployeeRead:
    return EmployeeRead(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        birth_date=employee.birth_date,
        phone_number=employee.phone_number,
        username=employee.username,
        email=employee.email,
        addresses=[_address_to_read(link) for link in employee.addresses],
        hire_date=employee.hire_date,
        termination_date=employee.termination_date,
        active=employee.active,
        last_login_at=employee.last_login_at,
        last_password_change_at=employee.last_password_change_at,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
    )


async def create_username(
    db: AsyncSession, first_name: str, last_name: str, birth_date: date
) -> str:
    user = f"{first_name[:2]}{last_name[:2]}{birth_date.strftime('%y')}".upper()

    stmt = select(func.count(Employee.id)).where(Employee.username.like(f"{user}%"))
    result = await db.execute(stmt)
    i = result.scalar() or 0
    user = f"{user}{i + 1:02d}"

    return user


async def create_employee(
    db: AsyncSession, data: EmployeeCreate
) -> EmployeeCreateResponse:
    data.first_name = data.first_name.strip().title()
    data.last_name = data.last_name.strip().title()
    data.phone_number = data.phone_number.strip()
    data.email = data.email.strip().lower() if data.email else None

    username = await create_username(
        db, data.first_name, data.last_name, data.birth_date
    )
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)

    employee = Employee(
        username=username,
        password=hashed_password,
        first_name=data.first_name,
        last_name=data.last_name,
        birth_date=data.birth_date,
        phone_number=data.phone_number,
        email=data.email,
    )
    db.add(employee)

    await db.commit()

    employee_read = await get_employee(db, employee.id)

    return EmployeeCreateResponse(
        **employee_read.model_dump(), temporary_password=plain_password
    )


async def employee_exists(db: AsyncSession, employee_id: UUID) -> bool:
    stmt = select(Employee.id).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    return employee is not None


async def _get_employee_orm(db: AsyncSession, employee_id: UUID) -> Employee:
    stmt = (
        select(Employee)
        .options(selectinload(Employee.addresses).selectinload(EmployeeAddress.address))
        .where(Employee.id == employee_id)
        .execution_options(populate_existing=True)
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise EmployeeNotFound

    return employee


async def get_employee(db: AsyncSession, employee_id: UUID) -> EmployeeRead:
    return _employee_to_read(await _get_employee_orm(db, employee_id))


async def list_employees(
    db: AsyncSession, include_inactive: bool = False
) -> list[EmployeeRead]:
    stmt = select(Employee).options(
        selectinload(Employee.addresses).selectinload(EmployeeAddress.address)
    )
    if not include_inactive:
        stmt = stmt.where(Employee.active.is_(True))
    result = await db.execute(stmt)

    return [_employee_to_read(employee) for employee in result.scalars().all()]


async def create_employee_address(
    db: AsyncSession,
    employee_id: UUID,
    address_data: AddressCreateBody,
    is_default: bool = False,
) -> EmployeeAddressRead:
    if not await employee_exists(db, employee_id):
        raise EmployeeNotFound

    address = Address(**address_data.model_dump())
    db.add(address)
    await db.flush()

    if is_default:
        await _clear_default_address(db, employee_id, address.id)

    employee_address = EmployeeAddress(
        employee_id=employee_id,
        address=address,
        is_default=is_default,
        active=True,
        activated_at=today(),
    )
    db.add(employee_address)

    await db.commit()
    await db.refresh(address)

    return _address_to_read(employee_address)


async def list_employee_addresses(
    db: AsyncSession, employee_id: UUID
) -> list[EmployeeAddressRead]:
    if not await employee_exists(db, employee_id):
        raise EmployeeNotFound

    stmt = (
        select(EmployeeAddress)
        .options(selectinload(EmployeeAddress.address))
        .where(EmployeeAddress.employee_id == employee_id)
    )
    result = await db.execute(stmt)

    return [_address_to_read(link) for link in result.scalars().all()]


async def _get_employee_address(
    db: AsyncSession, employee_id: UUID, address_id: UUID
) -> EmployeeAddress:
    stmt = (
        select(EmployeeAddress)
        .options(selectinload(EmployeeAddress.address))
        .where(
            EmployeeAddress.employee_id == employee_id,
            EmployeeAddress.address_id == address_id,
        )
    )
    link = (await db.execute(stmt)).scalar_one_or_none()

    if link is None:
        raise EmployeeAddressNotFound

    return link


async def _get_default_employee_address(
    db: AsyncSession, employee_id: UUID
) -> EmployeeAddress | None:
    stmt = select(EmployeeAddress).where(
        EmployeeAddress.employee_id == employee_id,
        EmployeeAddress.is_default.is_(True),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _clear_default_address(
    db: AsyncSession, employee_id: UUID, address_id: UUID
) -> None:
    current_default = await _get_default_employee_address(db, employee_id)
    if current_default is not None and current_default.address_id != address_id:
        current_default.is_default = False
        await db.flush()


async def update_employee_address(
    db: AsyncSession,
    employee_id: UUID,
    address_id: UUID,
    data: EmployeeAddressUpdateBody,
) -> EmployeeAddressRead:
    employee_address = await _get_employee_address(db, employee_id, address_id)
    address = employee_address.address

    update_data = data.model_dump(exclude_unset=True)
    is_default = update_data.pop("is_default", None)

    for field, value in update_data.items():
        setattr(address, field, value)

    if is_default is True:
        await _clear_default_address(db, employee_id, address_id)
        employee_address.is_default = True
    elif is_default is False:
        employee_address.is_default = False

    await db.commit()
    await db.refresh(address)

    return _address_to_read(employee_address)


async def delete_employee_address(
    db: AsyncSession, employee_id: UUID, address_id: UUID
) -> None:
    employee_address = await _get_employee_address(db, employee_id, address_id)

    employee_address.is_default = False
    employee_address.active = False
    employee_address.deactivated_at = today()

    await db.commit()


async def update_employee(
    db: AsyncSession, employee_id: UUID, data: EmployeeUpdate
) -> EmployeeRead:
    employee = await _get_employee_orm(db, employee_id)

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

    if "first_name" in update_data or "last_name" in update_data:
        update_data["username"] = await create_username(
            db,
            update_data.get("first_name", employee.first_name),
            update_data.get("last_name", employee.last_name),
            employee.birth_date,
        )

    for field, value in update_data.items():
        setattr(employee, field, value)

    await db.commit()

    return await get_employee(db, employee.id)


async def activate_employee(
    db: AsyncSession, employee_id: UUID, hire_date: date | None = None
) -> EmployeeRead:
    employee = await _get_employee_orm(db, employee_id)

    if employee.active:
        raise ActiveEmployee

    employee.active = True
    employee.hire_date = hire_date or today()
    employee.termination_date = None

    await db.commit()

    return await get_employee(db, employee.id)


async def deactivate_employee(
    db: AsyncSession, employee_id: UUID, termination_date: date | None = None
) -> EmployeeRead:
    employee = await _get_employee_orm(db, employee_id)

    if not employee.active:
        raise InactiveEmployee

    employee.active = False
    employee.termination_date = termination_date or today()

    await db.commit()

    return await get_employee(db, employee.id)


async def reset_employee_password(db: AsyncSession, employee_id: UUID) -> str:
    employee = await _get_employee_orm(db, employee_id)

    plain_password = generate_password()
    employee.password = hash_password(plain_password)
    employee.last_password_change_at = now()

    await db.commit()

    return plain_password


async def delete_employee(db: AsyncSession, employee_id: UUID) -> None:
    employee = await _get_employee_orm(db, employee_id)

    await db.delete(employee)
    await db.commit()
