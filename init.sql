CREATE EXTENSION vector;

CREATE TABLE IF NOT EXISTS job_vector (
    id INT PRIMARY KEY,
    job_title TEXT,
    job_title_vector vector(384)
);

CREATE TABLE IF NOT EXISTS job_classifier (
    id SERIAL PRIMARY KEY,
    job_title TEXT,
    associated_occupational_category TEXT,
    job_title_l12_embedding vector(384),
    job_title_flaubert_embedding vector(768)
);

CREATE TABLE IF NOT EXISTS search_result (
    job_title TEXT,
    similarity FLOAT
);

ALTER TABLE job_vector
    ADD COLUMN job_title_camembert_embedding vector(768);


ALTER TABLE job_vector
    RENAME COLUMN job_title_vector TO job_title_l12_embedding;

ALTER TABLE job_vector
    ADD COLUMN job_title_flaubert_embedding vector(768);

-- For L2 distance
CREATE INDEX job_vector_camembert_vector_idx ON job_vector USING hnsw (job_title_camembert_embedding vector_l2_ops);

-- For Inner Product
CREATE INDEX job_vector_camembert_vector_ip_idx ON job_vector USING hnsw (job_title_camembert_embedding vector_ip_ops);

-- Cosine similarity
CREATE INDEX job_vector_camembert_vector_cosine_idx ON job_vector USING hnsw (job_title_camembert_embedding vector_cosine_ops);


-- For L2 distance
CREATE INDEX job_vector_l12_vector_idx ON job_vector USING hnsw (job_title_l12_embedding vector_l2_ops);

-- For Inner Product
CREATE INDEX job_vector_l12_vector_ip_idx ON job_vector USING hnsw (job_title_l12_embedding vector_ip_ops);

-- Cosine similarity
CREATE INDEX job_vector_l12_vector_cosine_idx ON job_vector USING hnsw (job_title_l12_embedding vector_cosine_ops);

-- For L2 distance
CREATE INDEX job_classifier_l12_vector_idx ON job_classifier USING hnsw (job_title_l12_embedding vector_l2_ops);

-- For Inner Product
CREATE INDEX job_classifier_l12_vector_ip_idx ON job_classifier USING hnsw (job_title_l12_embedding vector_ip_ops);

-- Cosine similarity
CREATE INDEX job_classifier_l12_vector_cosine_idx ON job_classifier USING hnsw (job_title_l12_embedding vector_cosine_ops);

-- For L2 distance
CREATE INDEX job_classifier_flaubert_vector_idx ON job_classifier USING hnsw (job_title_flaubert_embedding vector_l2_ops);

-- For Inner Product
CREATE INDEX job_classifier_flaubert_vector_ip_idx ON job_classifier USING hnsw (job_title_flaubert_embedding vector_ip_ops);

-- Cosine similarity
CREATE INDEX job_classifier_flaubert_vector_cosine_idx ON job_classifier USING hnsw (job_title_flaubert_embedding vector_cosine_ops);
