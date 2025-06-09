from transformers import DPRContextEncoder, DPRContextEncoderTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import faiss
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, PASSAGE_ENCODER_NAME
from app.vector_store import save_faiss_index, load_faiss_index
import torch

ctx_tokenizer = DPRContextEncoderTokenizer.from_pretrained(PASSAGE_ENCODER_NAME)
ctx_encoder = DPRContextEncoder.from_pretrained(PASSAGE_ENCODER_NAME)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, a_min=1e-8, a_max=None)

def build_or_update_index(filename: str, text: str):
    print("Inside the build_or_update_index")
    chunks = text_splitter.split_text(text)
    
    inputs = ctx_tokenizer(chunks, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embeddings = ctx_encoder(**inputs).pooler_output
        #embeddings=ctx_encoder(**inputs).last_hidden_state[:, 0, :]

    embeddings = normalize(np.array(embeddings).astype("float32"))

    metadatas = [{"source": filename, "chunk_index": i, "text": chunk} for i, chunk in enumerate(chunks)]

    try:
        index, existing_metadata = load_faiss_index()
        index.add(embeddings)
        metadatas = existing_metadata + metadatas
    except Exception:
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

    save_faiss_index(index, metadatas)
    return len(chunks)
