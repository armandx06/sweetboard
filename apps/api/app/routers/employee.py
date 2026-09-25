from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import employee as crud_employee
from app.db.session import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeCreateResponse,
    EmployeeRead,
    EmployeeUpdate,
    PasswordResetResponse,
)

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeCreateResponse, status_code=201)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    return await crud_employee.create_employee(db, data)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    employee = await crud_employee.get_employee(db, employee_id)
    return employee


@router.get("", response_model=list[EmployeeRead])
async def list_employees(
    include_inactive: bool = False, db: AsyncSession = Depends(get_db)
):
    return await crud_employee.list_employees(db, include_inactive)


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: UUID, data: EmployeeUpdate, db: AsyncSession = Depends(get_db)
):
    employee = await crud_employee.update_employee(db, employee_id, data)
    return employee


@router.patch("/{employee_id}/deactivate", response_model=EmployeeRead)
async def deactivate_employee(
    employee_id: UUID,
    termination_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    employee = await crud_employee.deactivate_employee(
        db, employee_id, termination_date
    )
    return employee


@router.patch("/{employee_id}/activate", response_model=EmployeeRead)
async def activate_employee(
    employee_id: UUID, hire_date: date | None = None, db: AsyncSession = Depends(get_db)
):
    employee = await crud_employee.activate_employee(db, employee_id, hire_date)
    return employee


@router.post("/{employee_id}/reset-password", response_model=PasswordResetResponse)
async def reset_password(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await crud_employee.reset_employee_password(db, employee_id)
    plain_password = result
    return PasswordResetResponse(temporary_password=plain_password)


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    await crud_employee.delete_employee(db, employee_id)
