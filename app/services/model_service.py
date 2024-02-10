from typing import List
from sentence_transformers import SentenceTransformer
from transformers import CamembertModel, CamembertTokenizer
import torch

l12model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
tokenizer = CamembertTokenizer.from_pretrained("camembert-base")
camembertmodel = CamembertModel.from_pretrained("camembert-base")


def texts_to_vectors(texts: List[str]) -> List[List[float]]:
    embeddings = l12model.encode(texts, convert_to_tensor=False)
    return embeddings.tolist()

def get_camembert_embeddings(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = camembertmodel(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
    return embeddings