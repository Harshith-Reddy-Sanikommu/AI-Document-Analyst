# AI Document Analyst

A small retrieval-augmented document question-answering application built with FastAPI, Streamlit, TF-IDF retrieval, and a hosted open-weight language model API.

## Features

- PDF, TXT, and Markdown uploads
- Text extraction and overlapping chunk creation
- TF-IDF ranking to send only relevant chunks to the model
- Source labels with page and chunk identifiers
- Evidence-only answer instructions and an unknown-answer fallback
- In-memory answer caching and response latency display
- API input validation, readable errors, and basic tests

## Requirements

- Python 3.12 recommended
- A Hugging Face access token with Inference Providers permission
- Internet access for model requests

## Windows / VS Code setup

Open this folder in VS Code. In the integrated PowerShell terminal:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace `HF_TOKEN` with your token. Never commit `.env` or paste the token into source code.

## Run locally

Terminal 1 — API:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to inspect the API.

Terminal 2 — UI:

```powershell
streamlit run frontend.py
```

The app opens at the local URL printed by Streamlit. The UI expects the API at `http://127.0.0.1:8000` by default; set `API_URL` if it differs.

## Run tests

```powershell
pytest -q
```

## Model choice

The starter configuration uses `openai/gpt-oss-120b:fastest` through Hugging Face's OpenAI-compatible Inference Providers endpoint. This keeps model inference outside the application server, avoiding the hardware and setup costs of hosting a large model locally. Availability and usage limits depend on the selected provider and account. The model can be changed using `MODEL_NAME` in `.env`.

## Architecture

1. Streamlit collects uploads and questions.
2. FastAPI validates uploads and questions.
3. `document_parser.py` extracts text from PDF or UTF-8 text files.
4. `retrieval.py` splits content into overlapping chunks and ranks them with TF-IDF/cosine similarity.
5. `answering.py` sends only selected passages to the model, asks it to abstain when evidence is missing, and caches repeated question/context pairs.
6. FastAPI returns the answer and the exact retrieved passages as source evidence.

## Limitations and next steps

- Scanned PDFs require OCR; this MVP intentionally reports that limitation.
- Documents are stored in process memory and disappear when the API restarts.
- TF-IDF is lexical retrieval, not semantic embedding search.
- In-memory caching is per process and resets on restart.
- For production, add authentication, per-user document isolation, upload rate limits, persistent storage, restricted CORS origins, and privacy-aware retention policies.

## Measuring the optimization

Run the same question twice against the same uploaded document. The first request may call the model; the second can reuse the cached completion. Record first and second response latency in a small table and report actual observed values. Do not invent performance numbers. Also compare prompt context size with the full extracted document size if you want to quantify retrieval's token-saving effect.
