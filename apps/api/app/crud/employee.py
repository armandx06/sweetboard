from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate


async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
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
