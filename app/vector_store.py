import faiss
import pickle
from app.config import FAISS_INDEX_PATH

def save_faiss_index(index, metadata):
    FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH / "index.faiss"))
    with open(FAISS_INDEX_PATH / "metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

def load_faiss_index():
    index_path = FAISS_INDEX_PATH / "index.faiss"
    metadata_path = FAISS_INDEX_PATH / "metadata.pkl"
    print("inside load_faiss_index")
    print(index_path)
    print(metadata_path)
    if not index_path.exists() or not metadata_path.exists():
        print("⚠️ FAISS index or metadata file not found.")
        return None, []    
    index = faiss.read_index(str(FAISS_INDEX_PATH / "index.faiss"))
    with open(FAISS_INDEX_PATH / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    return index, metadata
