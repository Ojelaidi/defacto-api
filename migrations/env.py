from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base import Base

# Alembic Configurations
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# Database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Async Engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)
