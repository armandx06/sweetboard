from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_password, hash_password
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeCreateResponse


async def create_employee(
    db: AsyncSession, data: EmployeeCreate
) -> EmployeeCreateResponse:
    data.first_name = data.first_name.strip().title()
    data.last_name = data.last_name.strip().title()
    data.phone_number = data.phone_number.strip()
    data.email = data.email.strip().lower() if data.email else None

    user = f"{data.first_name[:2]}{data.last_name[:2]}{data.birth_date.strftime('%y')}".upper()
    stmt = select(func.count(Employee.id)).where(Employee.username.like(f"{user}%"))
    result = await db.execute(stmt)
    i = result.scalar() or 0
    username = f"{user}{i + 1:02d}"
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


async def list_employees(db: AsyncSession) -> list[Employee]:
    stmt = select(Employee)
    result = await db.execute(stmt)
    return list(result.scalars().all())
