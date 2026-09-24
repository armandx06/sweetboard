from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_password
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate


async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    data.first_name = data.first_name.strip().title()
    data.last_name = data.last_name.strip().title()
    data.phone_number = data.phone_number.strip()
    data.email = data.email.strip().lower() if data.email else None

    user = f"{data.first_name[:2]}{data.last_name[:2]}{data.birth_date.strftime('%y')}"
    stmt = select(func.count(Employee.id)).where(Employee.username.like(f"{user}%"))
    result = await db.execute(stmt)
    i = result.scalar() or 0
    data.username = f"{user}{i + 1:02d}".upper()
    data.password = generate_password()

    employee = Employee(**data.model_dump())
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee


async def get_employee(db: AsyncSession, employee_id: UUID) -> Employee | None:
    stmt = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_employees(db: AsyncSession) -> list[Employee]:
    stmt = select(Employee)
    result = await db.execute(stmt)
    return list(result.scalars().all())
