from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import employee as crud_employee
from app.db.session import get_db
from app.schemas.address import (
    AddressCreateBody,
    EmployeeAddressRead,
    EmployeeAddressUpdateBody,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeCreateResponse,
    EmployeeRead,
    EmployeeUpdate,
    PasswordResetResponse,
)

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "",
    response_model=EmployeeCreateResponse,
    status_code=201,
    summary="Create a new employee",
    description="Create a new employee with the provided details.",
)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    return await crud_employee.create_employee(db, data)


@router.post(
    "/{employee_id}/addresses",
    response_model=EmployeeAddressRead,
    status_code=201,
    summary="Create a new employee address",
    description="Creates a new address with the provided details for an employee.",
)
async def create_employee_address(
    employee_id: UUID,
    address_data: AddressCreateBody,
    is_default: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_employee.create_employee_address(
        db, employee_id, address_data, is_default
    )


@router.get(
    "/{employee_id}/addresses",
    response_model=list[EmployeeAddressRead],
    summary="List employee addresses",
    description="Retrieve all addresses linked to an employee.",
)
async def list_employee_addresses(
    employee_id: UUID, db: AsyncSession = Depends(get_db)
):
    return await crud_employee.list_employee_addresses(db, employee_id)


@router.patch(
    "/{employee_id}/addresses/{address_id}",
    response_model=EmployeeAddressRead,
    summary="Update an employee address",
    description="Update an address linked to an employee and its link flags.",
)
async def update_employee_address(
    employee_id: UUID,
    address_id: UUID,
    data: EmployeeAddressUpdateBody,
    db: AsyncSession = Depends(get_db),
):
    return await crud_employee.update_employee_address(
        db, employee_id, address_id, data
    )


@router.delete(
    "/{employee_id}/addresses/{address_id}",
    status_code=204,
    summary="Remove an employee address",
    description=(
        "Unlink the address from the employee. The address is deleted only when "
        "no other customer, supplier, or employee still uses it."
    ),
)
async def delete_employee_address(
    employee_id: UUID, address_id: UUID, db: AsyncSession = Depends(get_db)
):
    await crud_employee.delete_employee_address(db, employee_id, address_id)


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Get an employee",
    description="Retrieve the details of a specific employee.",
)
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    employee = await crud_employee.get_employee(db, employee_id)
    return employee


@router.get(
    "",
    response_model=list[EmployeeRead],
    summary="List employees",
    description="Retrieve a list of all employees, including inactive ones if specified.",
)
async def list_employees(
    include_inactive: bool = False, db: AsyncSession = Depends(get_db)
):
    return await crud_employee.list_employees(db, include_inactive)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Update an employee",
    description="Update the contact details of an existing employee.",
)
async def update_employee(
    employee_id: UUID, data: EmployeeUpdate, db: AsyncSession = Depends(get_db)
):
    return await crud_employee.update_employee(db, employee_id, data)


@router.patch(
    "/{employee_id}/activate",
    response_model=EmployeeRead,
    summary="Activate an employee",
    description="Activate an existing inactive employee with the provided details.",
)
async def activate_employee(
    employee_id: UUID, hire_date: date | None = None, db: AsyncSession = Depends(get_db)
):
    return await crud_employee.activate_employee(db, employee_id, hire_date)


@router.patch(
    "/{employee_id}/deactivate",
    response_model=EmployeeRead,
    summary="Deactivate an employee",
    description="Deactivate an existing active employee with the provided details (soft delete).",
)
async def deactivate_employee(
    employee_id: UUID,
    termination_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud_employee.deactivate_employee(db, employee_id, termination_date)


@router.post(
    "/{employee_id}/reset-password",
    response_model=PasswordResetResponse,
    summary="Reset employee password",
    description="Reset the password for an existing employee.",
)
async def reset_password(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await crud_employee.reset_employee_password(db, employee_id)
    plain_password = result
    return PasswordResetResponse(temporary_password=plain_password)


@router.delete(
    "/{employee_id}",
    status_code=204,
    summary="Delete an employee",
    description="Delete an existing employee (hard delete).",
)
async def delete_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    await crud_employee.delete_employee(db, employee_id)
