from time import perf_counter
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import AskRequest, AskResponse, SourceChunk
from app.services.document_parser import DocumentParseError, extract_text
from app.services.retrieval import Chunk, split_into_chunks, retrieve_chunks
from app.services.answering import (
    ModelConfigurationError, ModelRequestError, answer_question
)

app = FastAPI(title="AI Document Analyst API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to the deployed frontend domain for production.
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# MVP storage: documents live in memory and disappear when the API restarts.
documents: dict[str, dict] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "AI Document Analyst API"}

@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    filename = (file.filename or "").strip()
    if not filename or "." not in filename:
        raise HTTPException(status_code=400, detail="Please upload a PDF, TXT, or MD file.")
    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.max_upload_mb} MB limit.")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    try:
        segments = extract_text(filename, content)
        chunks = split_into_chunks(
            segments, filename, settings.chunk_size, settings.chunk_overlap
        )
    except DocumentParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not chunks:
        raise HTTPException(status_code=422, detail="No usable text was extracted from this document.")
    document_id = str(uuid4())
    documents[document_id] = {"filename": filename, "chunks": chunks}
    return {
        "document_id": document_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "message": "Document processed successfully.",
    }

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    document = documents.get(request.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found. Upload it again and retry.")
    started = perf_counter()
    selected = retrieve_chunks(
        request.question,
        document["chunks"],
        request.top_k or settings.retrieval_top_k,
    )
    try:
        answer, model_latency_ms, cached = answer_question(request.question, selected)
    except ModelConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ModelRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    sources = [
        SourceChunk(source=c.source, page=c.page, chunk_id=c.chunk_id, text=c.text)
        for c in selected
    ]
    elapsed = (perf_counter() - started) * 1000
    return AskResponse(
        answer=answer,
        sources=sources,
        latency_ms=round(model_latency_ms if model_latency_ms else elapsed, 2),
        cached=cached,
    )
