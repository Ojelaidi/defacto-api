from typing import List
from sentence_transformers import SentenceTransformer

l12model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def texts_to_vectors(texts: List[str]) -> List[List[float]]:
    embeddings = l12model.encode(texts, convert_to_tensor=False)
    return embeddings.tolist()
