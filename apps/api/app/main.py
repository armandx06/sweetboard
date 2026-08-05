from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

app = FastAPI(title="Sweetboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    db_result: int


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    result = await db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", db_result=result.scalar_one())
