from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import JobVector
from app.schemas.schemas import JobVectorCreate


async def create_vector(db: AsyncSession, *, obj_in: JobVectorCreate) -> JobVector:
    db_obj = JobVector(**obj_in.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
