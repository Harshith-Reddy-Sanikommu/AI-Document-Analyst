
import hashlib
import time
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings
from app.services.retrieval import Chunk


class ModelConfigurationError(RuntimeError):
    pass


class ModelRequestError(RuntimeError):
    pass


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise ModelConfigurationError(
            "Gemini is not configured. Add GEMINI_API_KEY to your .env file."
        )

    return genai.Client(api_key=settings.gemini_api_key)


@lru_cache(maxsize=128)
def _cached_completion(
    cache_key: str,
    question: str,
    context: str,
) -> str:
    client = _client()

    system_instruction = (
        "You are an AI document analyst. Answer using only the supplied "
        "document excerpts. If the excerpts do not contain enough evidence, "
        "say exactly: 'I could not find enough information in the uploaded "
        "document to answer that.' Do not invent facts, page numbers, "
        "quotations, or citations. Be concise and accurate."
    )

    prompt = (
        f"DOCUMENT EXCERPTS:\n{context}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Answer using only the supplied excerpts."
    )

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0,
                max_output_tokens=500,
            ),
        )

        answer = response.text

        if not answer or not answer.strip():
            raise ModelRequestError(
                "Gemini returned an empty answer."
            )

        return answer.strip()

    except ModelRequestError:
        raise
    except Exception as exc:
        # Preserve the original error for server-side debugging.
        print(
            f"Gemini request failed: {type(exc).__name__}: {exc}"
        )
        raise ModelRequestError(
            "Gemini could not generate an answer. Check the API key, "
            "model availability, quota, and network connection."
        ) from exc


def answer_question(
    question: str,
    chunks: list[Chunk],
) -> tuple[str, float, bool]:
    if not chunks:
        return (
            "I could not find relevant information in the uploaded document "
            "to answer that.",
            0.0,
            False,
        )

    context = "\n\n".join(
        f"[Source: {chunk.source}; "
        f"page: {chunk.page if chunk.page is not None else 'not available'}; "
        f"chunk: {chunk.chunk_id}]\n{chunk.text}"
        for chunk in chunks
    )

    key_material = (
        f"{settings.gemini_model}\n{question.strip()}\n{context}"
    )
    cache_key = hashlib.sha256(
        key_material.encode("utf-8")
    ).hexdigest()

    previous_hits = _cached_completion.cache_info().hits
    started = time.perf_counter()

    answer = _cached_completion(
        cache_key,
        question.strip(),
        context,
    )

    latency_ms = (time.perf_counter() - started) * 1000
    cache_hit = (
        _cached_completion.cache_info().hits > previous_hits
    )

    return answer, latency_ms, cache_hit


def clear_answer_cache() -> None:
    _cached_completion.cache_clear()