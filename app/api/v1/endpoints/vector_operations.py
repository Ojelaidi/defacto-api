from app.schemas.schemas import JobVectorCreate, JobVector, SearchResult
from app.crud.crud_vector import create_vector
from app.schemas.schemas import TextList
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import SearchRequest
from app.api.v1.dependencies.database import get_db
from typing import List, Dict, Any
from app.services.vector_service import texts_to_vectors
from app.services.indexer_service import index_documents_from_json
from sqlalchemy import text

router = APIRouter()


@router.post("/vectors/", response_model=JobVector)
async def create_job_vector(vector: JobVectorCreate, db: AsyncSession = Depends(get_db)):
    return await create_vector(db=db, obj_in=vector)


@router.post("/vectorize_batch/", response_model=Dict[str, Any])
async def vectorize_batch(text_list: TextList):
    try:
        vectors = texts_to_vectors(text_list.texts)
        return {"vectors": vectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vectorize texts: {str(e)}")


@router.post("/search/", response_model=List[SearchResult])
async def search(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               vector <-> :query_vector AS similarity 
        FROM job_vector 
        ORDER BY similarity ASC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]

@router.post("/index/vectorjobs")
async def index_vector_jobs():
    json_file_path = 'resources/job_vectors.json'
    index_name = 'vector-jobs-read'
    index_documents_from_json(json_file_path, index_name)
    return {"message": "Indexing..", "status": 200}
