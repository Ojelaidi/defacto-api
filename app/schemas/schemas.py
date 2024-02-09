from pydantic import BaseModel
from typing import List


class JobVectorBase(BaseModel):
    job_title: str
    vector: List[float]


class JobVectorCreate(JobVectorBase):
    pass


class JobVector(JobVectorBase):
    id: int

    class Config:
        from_attributes = True


class TextList(BaseModel):
    texts: List[str]


class SearchRequest(BaseModel):
    query_text: str


class SearchResult(BaseModel):
    job_title: str
    similarity: float