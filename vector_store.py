import faiss
import pickle
#from config import FAISS_INDEX_PATH

from pathlib import Path

FAISS_INDEX_PATH = Path("/app/data/faiss_index")

#FAISS_INDEX_PATH = "/app/data/faiss_index"
def load_faiss_index():
    index = faiss.read_index(str(FAISS_INDEX_PATH / "index.faiss"))
    with open(FAISS_INDEX_PATH / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    return index, metadata