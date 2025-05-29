from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.embed_store import build_or_update_index
from app.retrieve import ask_question
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Form

app = FastAPI( 
    title="My API",
    description="API for doing awesome things",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url=None
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class IngestRequest(BaseModel):
    path: str
    file: UploadFile

class QueryRequest(BaseModel):
    query: str
    page_size: int = 5

@app.post("/ingest")
def ingest(
    file: UploadFile = File(...),
    path: str = Form(...)):
    return JSONResponse({
        "doc_id": "doc-id-created"
    })

    try:
        num_chunks = build_or_update_index(request.filename, request.text)
        return {"message": f"✅ {num_chunks} chunks stored for {request.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/query")
def query(request: QueryRequest):
    return JSONResponse([{
        "doc_id": "doc-id-found",
        "path": "example/path/to/document.txt",
    }])
    try:
        print(f"Received question: {request.question} | top_k: {request.top_k}")
        result = ask_question(request.question, request.top_k)
        print(f"Retrieved result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in /query endpoint: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
