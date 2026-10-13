from dataclasses import dataclass
from functools import lru_cache
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass(frozen=True)
class Chunk:
    source: str
    page: int | None
    chunk_id: int
    text: str

def split_into_chunks(segments: list[tuple[int | None, str]], source: str,
                      chunk_size: int = 900, overlap: int = 150) -> list[Chunk]:
    if chunk_size < 100 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Chunk overlap must be non-negative and smaller than chunk size.")
    chunks = []
    chunk_id = 0
    for page, segment in segments:
        # Split on paragraph boundaries first, then use character windows for long paragraphs.
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", segment) if p.strip()]
        for paragraph in paragraphs:
            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                text = paragraph[start:end].strip()
                if text:
                    chunks.append(Chunk(source, page, chunk_id, text))
                    chunk_id += 1
                if end == len(paragraph):
                    break
                start = end - overlap
    return chunks

def retrieve_chunks(question: str, chunks: list[Chunk], top_k: int = 4) -> list[Chunk]:
    """Rank chunks lexically with TF-IDF; fit only on this document's chunks."""
    if not question.strip() or not chunks:
        return []
    texts = [chunk.text for chunk in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform(texts + [question])
    except ValueError:
        return []
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(range(len(chunks)), key=lambda i: float(scores[i]), reverse=True)
    # Avoid returning unrelated zero-score chunks.
    selected = [chunks[i] for i in ranked[:top_k] if scores[i] > 0]
    return selected
