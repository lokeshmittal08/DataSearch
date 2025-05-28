from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME
from app.vector_store import save_faiss_index, load_faiss_index

model = SentenceTransformer(EMBEDDING_MODEL_NAME)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

def build_or_update_index(filename: str, text: str):
    chunks = text_splitter.split_text(text)
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    metadatas = [{
        "source": filename,
        "chunk_index": i,
        "text": chunk
    } for i, chunk in enumerate(chunks)]

    try:
        index, existing_metadata = load_faiss_index()
        index.add(embeddings)
        metadatas = existing_metadata + metadatas
    except Exception:
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

    save_faiss_index(index, metadatas)
    return len(chunks)
