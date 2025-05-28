from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer
import numpy as np
from app.vector_store import load_faiss_index
from app.config import QUERY_ENCODER_NAME
import torch


MIN_SCORE_THRESHOLD = 0.5
OVERFETCH_FACTOR = 3

query_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(QUERY_ENCODER_NAME)
query_encoder = DPRQuestionEncoder.from_pretrained(QUERY_ENCODER_NAME)
print("Calling retrieve.py")
index, metadata = load_faiss_index()
print("values of index",str(index))
print("values of metadata",str(metadata))


def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, a_min=1e-8, a_max=None)

def ask_question(question: str, top_k: int = 5):
    if index is None or metadata is None:
        raise ValueError("FAISS index or metadata not loaded.")

    try:
        inputs = query_tokenizer(question, return_tensors="pt")
        with torch.no_grad():
            embedding = query_encoder(**inputs).pooler_output
            #embedding = query_encoder(**inputs).last_hidden_state[:, 0, :]
        query_vec = normalize(embedding.numpy().astype("float32"))

        k_search = top_k * OVERFETCH_FACTOR
        D, I = index.search(np.array(query_vec), k_search)

        seen_sources = set()
        unique_contexts = []

        for score, idx in zip(D[0], I[0]):
            if idx == -1 or score < MIN_SCORE_THRESHOLD:
                continue
            meta = metadata[idx]
            source_id = meta.get("source")
            if source_id in seen_sources:
                continue
            seen_sources.add(source_id)
            unique_contexts.append(
                f"[Score: {score:.4f}] [From {source_id} - chunk {meta.get('chunk_index')}]:\n{meta.get('text', '')}"
            )
            if len(unique_contexts) >= top_k:
                break

        if not unique_contexts:
            return {"question": question, "matches": [], "message": "❌ No relevant documents found with sufficient confidence."}
        return {"question": question, "matches": unique_contexts}

    except Exception as e:
        print(f"❌ Retrieval failed: {str(e)}")
        raise e
