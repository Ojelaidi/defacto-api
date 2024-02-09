from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session


async def init_db() -> None:
    async with async_session() as session:
        pass
