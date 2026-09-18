from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import employee as crud_employee
from app.db.session import get_db
from app.schemas.employee import EmployeeCreate, EmployeeRead

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeRead, status_code=201)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    return await crud_employee.create_employee(db, data)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    employee = await crud_employee.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.get("", response_model=list[EmployeeRead])
async def list_employees(db: AsyncSession = Depends(get_db)):
    return await crud_employee.list_employees(db)
