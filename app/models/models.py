from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base import Base


class JobVector(Base):
    __tablename__ = "job_vector"
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, index=True)
    vector = Column(Float)
