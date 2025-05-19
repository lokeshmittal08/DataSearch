import numpy as np
from sentence_transformers import SentenceTransformer
from app.vector_store import load_faiss_index
from app.config import EMBEDDING_MODEL_NAME

model = SentenceTransformer(EMBEDDING_MODEL_NAME)
index, metadata = load_faiss_index()

def ask_question(question: str, top_k: int = 5):
    if index is None:
        raise ValueError("FAISS index not loaded.")    
    question_embedding = model.encode([question]).astype("float32")
    print(f"Encoded question shape: {question_embedding.shape}")    
    D, I = index.search(np.array(question_embedding), top_k)
    print(f"Top-k indices: {I}, distances: {D}")
    contexts = [
        f"[From {metadata[i]['source']} - chunk {metadata[i]['chunk_index']}]:\n{metadata[i].get('text', '')}"
        for i in I[0]
    ]
    print("Context passed to LLM:\n", contexts)
    return {
        "question": question,
        "matches": contexts
    }
