
from csv import Error
import pickle
from typing import Mapping, Optional, Union
from numbers import Number
import uuid
import chromadb
from httpx import delete
from singleton_decorator import singleton
from app.config import CHUNK_OVERLAP, CHUNK_SIZE
from libs.util import chunk_text_words, dd, text_to_hash

@singleton
class VectorStore:
    def __init__(self):
        self._client = chromadb.PersistentClient(path="/app/storage/",settings=chromadb.config.Settings(allow_reset=True))
        self._create_collection()
        
    # create chroma collection if it does not exist
    def _create_collection(self):
        try:
            self._collection = self._client.get_collection(name='all')
        except:
            self._collection = self._client.create_collection(name="all", metadata={"hnsw:space": "cosine"})

        
    def add(self, text: str, id:str|None=None, meta: Mapping[str, Optional[Union[str, int, float, bool]]]= {}) -> str:
        id = str(uuid.uuid4().hex) if id is None else id
        doc_hash = text_to_hash(text)
        chunks = chunk_text_words(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        for chunk in chunks:
            meta["_hash"] = doc_hash
            self._collection.add(documents=[chunk],metadatas=[meta], ids=[id])
        return id
    
    
    def query(self, text: str, result_count: int = 5, similarityThreshold=None):
        results = self._collection.query(
            query_texts=[text],
            n_results=result_count,
            include=["metadatas",  "distances","documents"]
        )
        results = [{'id': i, 'meta': m, 'distance': d, "doc":doc} for i, m, d, doc in zip(results['ids'][0], results['metadatas'][0], results['distances'][0], results['documents'][0])]
        if similarityThreshold is not None:
            results = [r for r in results if r['distance'] <= similarityThreshold]
        return results
        
    def reset(self):
        """Reset the vector store."""
        self._client.delete_collection(name="all")
        self._create_collection()
    