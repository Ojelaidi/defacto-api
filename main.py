from fastapi import FastAPI
from app.api.v1.endpoints import vector_operations
from app.db.base import Base
from sqlalchemy.ext.asyncio import AsyncEngine


async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title="Job Classifier API", version="1.0")

app.include_router(
    vector_operations.router,
    prefix="/api/v1",
    tags=["vector-operations"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
