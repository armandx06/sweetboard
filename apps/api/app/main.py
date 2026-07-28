from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

app = FastAPI(title="Sweetboard API")


class HealthResponse(BaseModel):
    status: str
    db_result: int


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    result = await db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", db_result=result.scalar_one())
