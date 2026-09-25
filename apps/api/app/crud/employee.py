from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime import now, today
from app.core.security import generate_password, hash_password
from app.exceptions.exceptions import InactiveEmployee
from app.models.employee import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeCreateResponse,
    EmployeeUpdate,
)


async def create_username(
    db: AsyncSession, first_name: str, last_name: str, birth_date: date
) -> str:
    user = f"{first_name[:2]}{last_name[:2]}{birth_date.strftime('%y')}".upper()

    stmt = select(func.count(Employee.id)).where(Employee.username == user)
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
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(employee)
    return EmployeeCreateResponse(
        **employee.__dict__, temporary_password=plain_password
    )


async def get_employee(db: AsyncSession, employee_id: UUID) -> Employee | None:
    stmt = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_employees(
    db: AsyncSession, include_inactive: bool = False
) -> list[Employee]:
    stmt = select(Employee)
    if not include_inactive:
        stmt = stmt.where(Employee.active.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_employee(
    db: AsyncSession, employee_id: UUID, data: EmployeeUpdate
) -> Employee | None:
    employee = await get_employee(db, employee_id)
    if employee is None:
        return None

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
    await db.refresh(employee)
    return employee


async def deactivate_employee(
    db: AsyncSession, employee_id: UUID, termination_date: date | None = None
) -> Employee | None:
    employee = await get_employee(db, employee_id)
    if employee is None:
        return None
    if employee.hire_date is None:
        raise InactiveEmployee
    employee.active = False
    employee.termination_date = termination_date or today()
    await db.commit()
    await db.refresh(employee)
    return employee


async def activate_employee(
    db: AsyncSession, employee_id: UUID, hire_date: date | None = None
) -> Employee | None:
    employee = await get_employee(db, employee_id)
    if employee is None:
        return None
    employee.active = True
    employee.hire_date = hire_date or today()
    employee.termination_date = None
    await db.commit()
    await db.refresh(employee)
    return employee


async def reset_employee_password(
    db: AsyncSession, employee_id: UUID
) -> tuple[Employee, str] | None:
    employee = await get_employee(db, employee_id)
    if employee is None:
        return None
    plain_password = generate_password()
    employee.password = hash_password(plain_password)
    employee.last_password_change_at = now()
    await db.commit()
    await db.refresh(employee)
    return employee, plain_password
