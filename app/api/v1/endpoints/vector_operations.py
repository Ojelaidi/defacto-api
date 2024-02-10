from app.models.models import JobVector
from app.schemas.schemas import JobVectorCreate, SearchResult
from app.crud.crud_vector import create_vector
from app.schemas.schemas import TextList
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import SearchRequest
from app.api.v1.dependencies.database import get_db
from typing import List, Dict, Any
from sqlalchemy import text
import json
from app.services.model_service import texts_to_vectors
from sqlalchemy.future import select

router = APIRouter()


@router.post("/vectorize_batch/", response_model=Dict[str, Any])
async def vectorize_batch(text_list: TextList):
    try:
        vectors = texts_to_vectors(text_list.texts)
        return {"vectors": vectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vectorize texts: {str(e)}")


@router.post("/search-l2/", response_model=List[SearchResult])
async def searchl2(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
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


@router.post("/search-inner/", response_model=List[SearchResult])
async def searchinner(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               (vector <#> :query_vector) * -1 AS similarity 
        FROM job_vector 
        ORDER BY similarity DESC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/search-cosine/", response_model=List[SearchResult])
async def searchcos(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               1 - (vector <=> :query_vector) AS similarity 
        FROM job_vector 
        ORDER BY similarity DESC
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.get("/vectorize_and_store_seo", response_model=Dict[str, str])
async def vectorize_and_store_seo(db: AsyncSession = Depends(get_db)):
    try:
        # Load data from file
        with open('jobs-seo-v2.json', 'r') as file:
            data = json.load(file)

        texts = list(data.keys())
        vectors = texts_to_vectors(texts)

        for text, vector in zip(texts, vectors):
            existing_vector = await db.execute(
                select(JobVector).where(JobVector.job_title == text)
            )
            existing_vector = existing_vector.scalars().first()

            if not existing_vector:
                job_vector = JobVectorCreate(job_title=text, vector=vector)
                await create_vector(db=db, obj_in=job_vector)

        await db.commit()
        return {"message": "Vectors stored successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectorize_and_store_rome/")
async def vectorize_and_store_rome(db: AsyncSession = Depends(get_db)):
    texts = []
    try:
        with open('extracted_texts.json', 'r') as file:
            texts = json.load(file)

        vectors = texts_to_vectors(texts)

        for label, vector in zip(texts, vectors):
            existing_vector = await db.execute(select(JobVector).where(JobVector.job_title == label))
            existing_vector = existing_vector.scalars().first()

            if not existing_vector:
                job_vector = JobVector(job_title=label, vector=vector)
                db.add(job_vector)

        await db.commit()
        return {"message": "Vectors stored successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error during vector storage: {str(e)}")
