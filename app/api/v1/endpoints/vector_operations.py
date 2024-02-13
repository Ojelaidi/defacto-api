from app.models.models import JobVector, JobClassifier
from app.schemas.schemas import JobVectorCreate, SearchResult, SeoSearchResult
from app.crud.crud_vector import create_vector
from app.schemas.schemas import TextList
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.schemas import SearchRequest
from app.api.v1.dependencies.database import get_db
from typing import List, Dict, Any
from app.services.indexer_service import index_documents_from_json
from sqlalchemy import text
import json
from app.services.model_service import texts_to_vectors, get_camembert_embeddings, get_flaubert_embeddings
from sqlalchemy.future import select
from sqlalchemy import update

router = APIRouter()


@router.post("/index/vectorjobs")
async def index_vector_jobs():
    json_file_path = 'resources/job_vectors.json'
    index_name = 'vector-jobs-read'
    index_documents_from_json(json_file_path, index_name)
    return {"message": "Indexing..", "status": 200}


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


@router.get("/vectorize_and_store_titles", response_model=Dict[str, str])
async def vectorize_and_store_titles(db: AsyncSession = Depends(get_db)):
    try:
        with open('flattened_jobs_with_categories.json', 'r') as file:
            titles_data = json.load(file)

        for item in titles_data:
            job_title = item['job_title']
            associated_occupational_category = item['associatedOccupationalCategory']

            # Calculate embeddings
            l12_embeddings = texts_to_vectors([job_title])[0]
            flaubert_embeddings = get_flaubert_embeddings([job_title])[0]

            query = select(JobClassifier).where(JobClassifier.job_title == job_title)
            result = await db.execute(query)
            existing_job = result.scalars().first()

            if existing_job:
                pass
            else:
                new_job = JobClassifier(
                    job_title=job_title,
                    associated_occupational_category=associated_occupational_category,
                    job_title_l12_embedding=l12_embeddings,
                    job_title_flaubert_embedding=flaubert_embeddings
                )
                db.add(new_job)
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


@router.post("/populate-camembert-embeddings/")
async def populate_camembert_embeddings(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        query = select(JobVector)
        result = await db.execute(query)
        job_vectors = result.scalars().all()

        for job_vector in job_vectors:
            if job_vector.job_title_camembert_embedding is None:
                embeddings = get_camembert_embeddings([job_vector.job_title])
                flattened_embeddings = embeddings.flatten().tolist()
                update_stmt = update(JobVector).where(JobVector.id == job_vector.id).values(
                    job_title_camembert_embedding=flattened_embeddings)
                await db.execute(update_stmt)

        await db.commit()
    return {"message": "CamemBERT embeddings populated successfully."}


@router.post("/populate-flaubert-embeddings/")
async def populate_flaubert_embeddings(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        query = select(JobVector)
        result = await db.execute(query)
        job_vectors = result.scalars().all()

        for job_vector in job_vectors:
            if job_vector.job_title_flaubert_embedding is None:
                embeddings = get_flaubert_embeddings([job_vector.job_title])
                flattened_embeddings = embeddings.flatten().tolist()
                update_stmt = update(JobVector).where(JobVector.id == job_vector.id).values(
                    job_title_flaubert_embedding=flattened_embeddings)
                await db.execute(update_stmt)

        await db.commit()
    return {"message": "FlauBERT embeddings populated successfully."}


@router.post("/vectorize_batch/", response_model=Dict[str, Any])
async def vectorize_batch(text_list: TextList):
    try:
        vectors = texts_to_vectors(text_list.texts)
        return {"vectors": vectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vectorize texts: {str(e)}")


@router.post("/classify-l12-l2/", response_model=List[SearchResult])
async def classifyl12l2(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               job_title_l12_embedding <-> :query_vector AS similarity 
        FROM job_vector 
        ORDER BY similarity ASC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/classify-l12-inner/", response_model=List[SearchResult])
async def classifyl12inner(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               (job_title_l12_embedding <#> :query_vector) * -1 AS similarity 
        FROM job_vector 
        ORDER BY similarity DESC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/classify-l12-cosine/", response_model=List[SearchResult])
async def classifyl12cos(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               1 - (job_title_l12_embedding <=> :query_vector) AS similarity 
        FROM job_vector 
        ORDER BY similarity DESC
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/classify-camembert-l2/", response_model=List[SearchResult])
async def classifycamembertl2(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = get_camembert_embeddings([search_request.query_text])

    sql_query = text("""
        SELECT job_title, 
               job_title_camembert_embedding <-> :query_vector AS similarity 
        FROM job_vector 
        ORDER BY similarity ASC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector.flatten().tolist())})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/classify-camembert-inner/", response_model=List[SearchResult])
async def classifycamembertinner(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = get_camembert_embeddings([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               (job_title_camembert_embedding <#> :query_vector) * -1 AS similarity 
        FROM job_vector 
        ORDER BY similarity DESC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector.flatten().tolist())})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/classify-camembert-cosine/", response_model=List[SearchResult])
async def classifycamembertcos(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = get_camembert_embeddings([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, 
               1 - (job_title_camembert_embedding <=> :query_vector) AS similarity 
        FROM job_vector 
        ORDER BY similarity DESC
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector.flatten().tolist())})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity} for job in job_titles]


@router.post("/seo/classify-l12-l2/", response_model=List[SeoSearchResult])
async def seoclassifyl12l2(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, associated_occupational_category AS rome,
               job_title_l12_embedding <-> :query_vector AS similarity 
        FROM job_classifier
        ORDER BY similarity ASC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()
    print(job_titles)

    return [{"job_title": job.job_title, "code_rome": job.rome, "similarity": job.similarity} for job in
            job_titles]


@router.post("/seo/classify-l12-inner/", response_model=List[SeoSearchResult])
async def seoclassifyl12inner(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, associated_occupational_category,
               (job_title_l12_embedding <#> :query_vector) * -1 AS similarity 
        FROM job_classifier 
        ORDER BY similarity DESC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity,
             "code_rome": job.associated_occupational_category} for job in job_titles]


@router.post("/seo/classify-l12-cosine/", response_model=List[SeoSearchResult])
async def seoclassifyl12cos(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = texts_to_vectors([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, associated_occupational_category,
               1 - (job_title_l12_embedding <=> :query_vector) AS similarity 
        FROM job_classifier 
        ORDER BY similarity DESC
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector)})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity,
             "code_rome": job.associated_occupational_category} for job in job_titles]


@router.post("/seo/classify-flaubert-l2/", response_model=List[SeoSearchResult])
async def seoclassifyflaubertl2(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = get_flaubert_embeddings([search_request.query_text])

    sql_query = text("""
        SELECT job_title, associated_occupational_category,
               job_title_flaubert_embedding <-> :query_vector AS similarity 
        FROM job_classifier 
        ORDER BY similarity ASC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector.flatten().tolist())})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity,
             "code_rome": job.associated_occupational_category} for job in job_titles]


@router.post("/seo/classify-flaubert-inner/", response_model=List[SeoSearchResult])
async def seoclassifyflaubertinner(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = get_flaubert_embeddings([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, associated_occupational_category,
               (job_title_flaubert_embedding <#> :query_vector) * -1 AS similarity 
        FROM job_classifier 
        ORDER BY similarity DESC 
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector.flatten().tolist())})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity,
             "code_rome": job.associated_occupational_category} for job in job_titles]


@router.post("/seo/classify-flaubert-cosine/", response_model=List[SeoSearchResult])
async def seoclassifyflaubertcos(search_request: SearchRequest, db: AsyncSession = Depends(get_db)):
    if not search_request.query_text:
        raise HTTPException(status_code=400, detail="Query text is required.")

    query_vector = get_flaubert_embeddings([search_request.query_text])[0]

    sql_query = text("""
        SELECT job_title, associated_occupational_category,
               1 - (job_title_flaubert_embedding <=> :query_vector) AS similarity 
        FROM job_classifier 
        ORDER BY similarity DESC
        LIMIT 10;
    """)

    result = await db.execute(sql_query, {"query_vector": str(query_vector.flatten().tolist())})
    job_titles = result.fetchall()

    return [{"job_title": job.job_title, "similarity": job.similarity,
             "code_rome": job.associated_occupational_category} for job in job_titles]
