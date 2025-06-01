from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.embed_store import build_or_update_index
from app.retrieve import ask_question
from fastapi.middleware.cors import CORSMiddleware
from app.pdf_utils import extract_text_from_pdf  # You'll create this

app = FastAPI(    title="DPR-Based Document Search API",
    description="Ingest documents and ask questions using Dense Passage Retrieval.",
    version="1.0.0")

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
    pdf_file: UploadFile = File(...),
    ):
    try:
        # Save the file to disk
        file_location = f"/app/data/uploads/{filename}"
        with open(file_location, "wb") as f:
            f.write(await pdf_file.read())

        # Extract text
        text = extract_text_from_pdf(file_location)
        if not text:
            raise HTTPException(status_code=500, detail="Text extraction failed.")

        # Call existing function
        num_chunks = build_or_update_index(filename, text)
        return {"message": f"✅ {num_chunks} chunks stored for {filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    # try:
    #     num_chunks = build_or_update_index(request.filename, request.text)
    #     return {"message": f"✅ {num_chunks} chunks stored for {request.filename}"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/query")
def query(request: QueryRequest):
    try:
        print(f"Received question: {request.question} | top_k: {request.top_k}")
        result = ask_question(request.question, request.top_k)
        print(f"Retrieved result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in /query endpoint: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
