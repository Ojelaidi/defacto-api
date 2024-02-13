from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from pgvector.sqlalchemy import Vector


class JobVector(Base):
    __tablename__ = "job_vector"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, unique=False)
    job_title_l12_embedding = mapped_column(Vector(384))
    job_title_camembert_embedding = mapped_column(Vector(768))
    job_title_flaubert_embedding = mapped_column(Vector(768))


class JobClassifier(Base):
    __tablename__ = "job_classifier"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, unique=True)
    associated_occupational_category = Column(String, unique=False)
    job_title_l12_embedding = mapped_column(Vector(384))
    job_title_flaubert_embedding = mapped_column(Vector(768))
