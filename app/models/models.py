from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from pgvector.sqlalchemy import Vector


class JobVector(Base):
    __tablename__ = "job_vector"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, unique=False)
    vector = mapped_column(Vector(384))
