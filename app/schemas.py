from pydantic import BaseModel, Field

class SourceChunk(BaseModel):
    source: str
    page: int | None = None
    chunk_id: int
    text: str

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    document_id: str = Field(min_length=1, max_length=100)
    top_k: int | None = Field(default=None, ge=1, le=8)

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    latency_ms: float
    cached: bool
