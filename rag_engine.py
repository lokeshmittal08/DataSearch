import numpy as np
#from config import EMBEDDING_MODEL_NAME
from sentence_transformers import SentenceTransformer
from vector_store import load_faiss_index
from llm import generate_answer


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

index, metadata = load_faiss_index()


def ask_question(question: str, top_k: int = 5):
    
    question_embedding = model.encode([question])
    D, I = index.search(np.array(question_embedding), top_k)

    retrieved_contexts = [
        f"[From {metadata[i]['source']} - chunk {metadata[i]['chunk_index']}]:\n" + metadata[i].get('text', '')
        for i in I[0]
    ]

    # Use metadata to retrieve full context from chunks (optional)
    context = "\n---\n".join(retrieved_contexts)
    print("Context passed to LLM:\n", context)
    #return generate_answer(context, question)