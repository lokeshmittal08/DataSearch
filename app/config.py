from pathlib import Path

DOCUMENTS_PATH = Path("/app/data/documents")
FAISS_INDEX_PATH = Path("/app/data/faiss_index")
CHUNK_SIZE = 200
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "intfloat/e5-base-v2"
QUERY_ENCODER_NAME = "facebook/dpr-question_encoder-single-nq-base"
PASSAGE_ENCODER_NAME = "facebook/dpr-ctx_encoder-single-nq-base"
TEMP_STORAGE = "/tmp"
SIMILARITY_THRESHOLD = 0.7
