
from csv import Error
import pickle
from typing import Mapping, Optional, Union
from numbers import Number
import uuid
import chromadb
from httpx import delete
from singleton_decorator import singleton
from app.config import CHUNK_OVERLAP, CHUNK_SIZE,PASSAGE_ENCODER_NAME, QUERY_ENCODER_NAME
from libs.util import chunk_text_words, dd, text_to_hash
from transformers import logging, DPRContextEncoder, DPRContextEncoderTokenizer, DPRQuestionEncoder, DPRQuestionEncoderTokenizer
import torch

@singleton
class VectorStore:
    def __init__(self):
        logging.set_verbosity_error()
        self._client = chromadb.PersistentClient(path="/app/storage/",settings=chromadb.config.Settings(allow_reset=True))
        self._create_collection()
                # Load DPR models
        self.ctx_tokenizer = DPRContextEncoderTokenizer.from_pretrained(PASSAGE_ENCODER_NAME)
        self.ctx_encoder = DPRContextEncoder.from_pretrained(PASSAGE_ENCODER_NAME)
        self.q_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(QUERY_ENCODER_NAME)
        self.q_encoder = DPRQuestionEncoder.from_pretrained(QUERY_ENCODER_NAME)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ctx_encoder = self.ctx_encoder.to(self.device)
        self.q_encoder = self.q_encoder.to(self.device)
    # create chroma collection if it does not exist
    def _create_collection(self):
        try:
            self._collection = self._client.get_collection(name='all')
        except:
            self._collection = self._client.create_collection(name="all", metadata={"hnsw:space": "cosine"})

    def _embed_passages(self, passages: list[str]) -> list[list[float]]:
        inputs = self.ctx_tokenizer(passages, padding=True, truncation=True, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embeddings = self.ctx_encoder(**inputs).pooler_output
        return embeddings.cpu().tolist()

    def _embed_query(self, question: str) -> list[float]:
        inputs = self.q_tokenizer(question, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embedding = self.q_encoder(**inputs).pooler_output
        return embedding[0].cpu().tolist()
        
    def add(self, text: str, id:str|None=None, meta: Mapping[str, Optional[Union[str, int, float, bool]]]= {}) -> str:
        id = str(uuid.uuid4().hex) if id is None else id
        doc_hash = text_to_hash(text)
        chunks = chunk_text_words(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        embeddings = self._embed_passages(chunks)
        for chunk, embedding in zip(chunks, embeddings):
            meta["_hash"] = doc_hash
            self._collection.add(documents=[chunk], embeddings=[embedding], metadatas=[meta], ids=[id])
        return id        
        # for chunk in chunks:
        #     meta["_hash"] = doc_hash
        #     self._collection.add(documents=[chunk],metadatas=[meta], ids=[id])
        # return id
    
    
    def query(self, text: str, result_count: int = 5, similarityThreshold=None):
        embedding = self._embed_query(text)
        overfetch_k = result_count * 3  # I have added to reduce false negatives by enabling post processing deduplication and score filtering


        results = self._collection.query(
            query_embeddings=[embedding],
            #query_texts=[text],
            #n_results=result_count,
            n_results=overfetch_k,
            #where={"_hash": {"$ne": None}},  # Exclude documents without a hash
            include=["metadatas",  "distances","documents"]
        )
        # results = [{'id': i, 'meta': m, 'distance': d, "doc":doc} for i, m, d, doc in zip(results['ids'][0], results['metadatas'][0], results['distances'][0], results['documents'][0])]
        # if similarityThreshold is not None:
        #     results = [r for r in results if r['distance'] <= similarityThreshold]
        # return results
        seen_hashes = set()
        filtered = []
        similarityThreshold=0.7
        for i, m, d, doc in zip(results['ids'][0], results['metadatas'][0], results['distances'][0], results['documents'][0]):
            if d > (similarityThreshold if similarityThreshold else 0.7):
                continue
            doc_hash = m.get("_hash")
            if doc_hash in seen_hashes:
                continue
            seen_hashes.add(doc_hash)
            filtered.append({
                'id': i,
                'meta': m,
                'distance': d,
                'doc': doc
            })
            print(f"[DEBUG] Match Score: {1 - d:.4f}, Distance: {d:.4f}, ID: {i}")

            if len(filtered) >= result_count:
                break

        return filtered
        
    def reset(self):
        """Reset the vector store."""
        self._client.delete_collection(name="all")
        self._create_collection()
    