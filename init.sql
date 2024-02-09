CREATE EXTENSION vector;

CREATE TABLE IF NOT EXISTS job_vector (
    id INT PRIMARY KEY,
    job_title TEXT,
    job_title_vector vector(300)
);

CREATE TABLE IF NOT EXISTS search_result (
    job_title TEXT,
    similarity FLOAT
);