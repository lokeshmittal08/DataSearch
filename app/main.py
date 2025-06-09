from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.pdf_utils import extract_text_from_pdf
from libs.VectorStore import VectorStore  # You'll create this
from libs.util import uploaded_file_to_local
app = FastAPI(    title="DPR-Based Document Search API",
    description="Ingest documents and ask questions using Dense Passage Retrieval.",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class IngestRequest(BaseModel):
    filename: str
    text: str

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

@app.post("/ingest")
async def ingest_pdf(
    #request: IngestRequest
    filename: str = Form(...),
    pdf_file: UploadFile = File(...)
    ):
    print("Ingesting PDF file:", filename)
    text = extract_text_from_pdf(uploaded_file_to_local(pdf_file))
    vector_store = VectorStore()
    id = vector_store.add(text=text, meta={"filename": filename})
    return id
    
@app.post("/query")
def query(request: QueryRequest):
    vector_store = VectorStore()
    results = vector_store.query(text=request.question, result_count=request.top_k)
    return results