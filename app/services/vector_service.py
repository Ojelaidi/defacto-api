from sentence_transformers import SentenceTransformer
from typing import List

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def texts_to_vectors(texts: List[str]) -> List[List[float]]:
    embeddings = model.encode(texts, convert_to_tensor=False)
    return embeddings.tolist()
