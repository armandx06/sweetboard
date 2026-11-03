from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import customer as crud_customer
from app.db.session import get_db
from app.schemas.address import (
    AddressCreateBody,
    CustomerSupplierAddressRead,
    CustomerSupplierAddressUpdateBody,
)
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "",
    response_model=CustomerRead,
    status_code=201,
    summary="Create a new customer",
    description="Creates a new customer with the provided details.",
)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await crud_customer.create_customer(db, data)


@router.post(
    "/{customer_id}/addresses",
    response_model=CustomerSupplierAddressRead,
    status_code=201,
    summary="Create a new customer address",
    description="Creates a new address with the provided details for a customer.",
)
async def create_customer_address(
    customer_id: UUID,
    address_data: AddressCreateBody,
    is_default: bool = False,
    is_billing: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await crud_customer.create_customer_address(
        db, customer_id, address_data, is_default, is_billing
    )


@router.get(
    "/{customer_id}/addresses",
    response_model=list[CustomerSupplierAddressRead],
    summary="List customer addresses",
    description="Retrieve all addresses linked to a customer.",
)
async def list_customer_addresses(
    customer_id: UUID, db: AsyncSession = Depends(get_db)
):
    return await crud_customer.list_customer_addresses(db, customer_id)


@router.patch(
    "/{customer_id}/addresses/{address_id}",
    response_model=CustomerSupplierAddressRead,
    summary="Update a customer address",
    description="Update an address linked to a customer and its link flags.",
)
async def update_customer_address(
    customer_id: UUID,
    address_id: UUID,
    data: CustomerSupplierAddressUpdateBody,
    db: AsyncSession = Depends(get_db),
):
    return await crud_customer.update_customer_address(
        db, customer_id, address_id, data
    )


@router.delete(
    "/{customer_id}/addresses/{address_id}",
    status_code=204,
    summary="Remove a customer address",
    description=(
        "Unlink the address from the customer. The link is deactivated (soft "
        "delete) and its flags are cleared; the address row is kept and may still "
        "be used by other subjects."
    ),
)
async def delete_customer_address(
    customer_id: UUID, address_id: UUID, db: AsyncSession = Depends(get_db)
):
    await crud_customer.delete_customer_address(db, customer_id, address_id)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Get customer by ID",
    description="Retrieves a customer by their unique ID.",
)
async def get_customer(customer_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud_customer.get_customer(db, customer_id)


@router.get(
    "",
    response_model=list[CustomerRead],
    summary="List customers",
    description="Retrieve a list of all customers, including inactive ones if specified.",
)
async def list_customers(
    include_inactive: bool = False, db: AsyncSession = Depends(get_db)
):
    return await crud_customer.list_customers(db, include_inactive)


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Update a customer",
    description="Update the details of an existing customer.",
)
async def update_customer(
    customer_id: UUID, data: CustomerUpdate, db: AsyncSession = Depends(get_db)
):
    return await crud_customer.update_customer(db, customer_id, data)


@router.patch(
    "/{customer_id}/activate",
    response_model=CustomerRead,
    summary="Activate a customer",
    description="Activate an existing inactive customer with the provided details.",
)
async def activate_customer(
    customer_id: UUID,
    activated_at: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud_customer.activate_customer(db, customer_id, activated_at)


@router.patch(
    "/{customer_id}/deactivate",
    response_model=CustomerRead,
    summary="Deactivate a customer",
    description="Deactivate an existing active customer with the provided details (soft delete).",
)
async def deactivate_customer(
    customer_id: UUID,
    deactivated_at: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud_customer.deactivate_customer(db, customer_id, deactivated_at)


@router.delete(
    "/{customer_id}",
    status_code=204,
    summary="Delete a customer",
    description="Permanently delete an existing customer (hard delete).",
)
async def delete_customer(customer_id: UUID, db: AsyncSession = Depends(get_db)):
    await crud_customer.delete_customer(db, customer_id)
