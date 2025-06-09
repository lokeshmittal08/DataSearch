
from singleton_decorator import singleton

from app.config import SIMILARITY_THRESHOLD
from app.pdf_utils import extract_text_from_pdf
from libs.TextCleaner import TextCleaner
from libs.AnyFileParser import AnyFileParser
from libs.VectorStore import VectorStore
from models import FileInfo


@singleton
class Api:
    def __init__(self):
        pass
    
    def ingest(self,
               local_file_path: str, 
               meta: str, 
               vector_store:VectorStore=VectorStore(), 
               text_cleaner=TextCleaner(),
               file_parser=AnyFileParser()) -> str:

        text = file_parser.parse(local_file_path)
        text = text_cleaner.clean(text)
        id = vector_store.add(text=text, meta=meta)
        return id
    
    def query(self,
               question: str,
               top_k: int = 5,
               vector_store:VectorStore=VectorStore(),
               text_cleaner=TextCleaner()) -> list[FileInfo]:
          question = text_cleaner.clean(question)
          results = vector_store.query(text=question, result_count=top_k, similarityThreshold=SIMILARITY_THRESHOLD)
          return results
  