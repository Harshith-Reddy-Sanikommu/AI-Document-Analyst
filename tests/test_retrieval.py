from app.services.retrieval import split_into_chunks, retrieve_chunks

def test_chunking_preserves_source_and_page():
    chunks = split_into_chunks([(2, "alpha " * 250)], "sample.pdf", chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(chunk.source == "sample.pdf" for chunk in chunks)
    assert all(chunk.page == 2 for chunk in chunks)

def test_retrieval_returns_relevant_chunk():
    chunks = split_into_chunks(
        [(1, "The moon orbits Earth. Apples grow on trees.")],
        "facts.pdf",
        chunk_size=100,
        overlap=10,
    )
    results = retrieve_chunks("What orbits Earth?", chunks, top_k=1)
    assert results
    assert "moon" in results[0].text.lower()

def test_empty_question_returns_no_chunks():
    chunks = split_into_chunks([(None, "A short document.")], "note.txt")
    assert retrieve_chunks("   ", chunks) == []
