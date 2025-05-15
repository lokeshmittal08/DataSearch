from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import os
import pickle
#from config import DOCUMENTS_PATH, FAISS_INDEX_PATH, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME
from document_loader import load_documents
from pathlib import Path
DOCUMENTS_PATH = Path("/app/data/documents")

#DOCUMENTS_PATH ="/app/data/documents"
FAISS_INDEX_PATH = Path("/app/data/faiss_index")

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_PATH = "/app/model/mistral-7b.Q4_K_M.gguf" 

model = SentenceTransformer(EMBEDDING_MODEL_NAME)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)

def build_faiss_index():
    documents = load_documents(DOCUMENTS_PATH)
    texts = []
    metadatas = []

    for doc in documents:
        chunks = text_splitter.split_text(doc['content'])
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                "source": doc['file_path'],
                "chunk_index": i,
                "text": chunk
            })
    print(f"Loaded {len(texts)} text chunks.")
    if not texts:
        print("❌ No text chunks found. Check your documents.")
        return
    embeddings = model.encode(texts, show_progress_bar=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH / "index.faiss"))
    with open(FAISS_INDEX_PATH / "metadata.pkl", "wb") as f:
        pickle.dump(metadatas, f)

