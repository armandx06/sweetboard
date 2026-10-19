from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import supplier as crud_supplier
from app.db.session import get_db
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post(
    "",
    response_model=SupplierRead,
    status_code=201,
    summary="Create a new supplier",
    description="Creates a new supplier with the provided details.",
)
async def create_supplier(data: SupplierCreate, db: AsyncSession = Depends(get_db)):
    return await crud_supplier.create_supplier(db, data)


@router.get(
    "/{supplier_id}",
    response_model=SupplierRead,
    summary="Get supplier by ID",
    description="Retrieves a supplier by their unique ID.",
)
async def get_supplier(supplier_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud_supplier.get_supplier(db, supplier_id)


@router.get(
    "",
    response_model=list[SupplierRead],
    summary="List suppliers",
    description="Retrieve a list of all suppliers, including inactive ones if specified.",
)
async def list_suppliers(
    include_inactive: bool = False, db: AsyncSession = Depends(get_db)
):
    return await crud_supplier.list_suppliers(db, include_inactive)


@router.patch(
    "/{supplier_id}",
    response_model=SupplierRead,
    summary="Update a supplier",
    description="Update the details of an existing supplier.",
)
async def update_supplier(
    supplier_id: UUID, data: SupplierUpdate, db: AsyncSession = Depends(get_db)
):
    return await crud_supplier.update_supplier(db, supplier_id, data)


@router.patch(
    "/{supplier_id}/activate",
    response_model=SupplierRead,
    summary="Activate a supplier",
    description="Activate an existing inactive supplier with the provided details.",
)
async def activate_supplier(
    supplier_id: UUID,
    activated_at: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud_supplier.activate_supplier(db, supplier_id, activated_at)


@router.patch(
    "/{supplier_id}/deactivate",
    response_model=SupplierRead,
    summary="Deactivate a supplier",
    description="Deactivate an existing active supplier with the provided details (soft delete).",
)
async def deactivate_supplier(
    supplier_id: UUID,
    deactivated_at: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud_supplier.deactivate_supplier(db, supplier_id, deactivated_at)


@router.delete(
    "/{supplier_id}",
    status_code=204,
    summary="Delete a supplier",
    description="Permanently delete an existing supplier (hard delete).",
)
async def delete_supplier(supplier_id: UUID, db: AsyncSession = Depends(get_db)):
    await crud_supplier.delete_supplier(db, supplier_id)
