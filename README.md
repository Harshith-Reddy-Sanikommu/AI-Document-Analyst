# AI Document Analyst

An AI-powered application that allows users to upload documents, ask questions, and inspect the supporting evidence behind answers.

## Live Demo

* Frontend: https://ai-document-analyst-bsnfuzjpcdsb4asfebbosb.streamlit.app/
* Backend API: https://ai-document-analyst-rfu3.onrender.com
* API Health: https://ai-document-analyst-rfu3.onrender.com/health
* GitHub: https://github.com/Harshith-Reddy-Sanikommu/AI-Document-Analyst

## Features

* Upload PDF, TXT, and Markdown documents.
* Extract text and divide it into overlapping chunks.
* Retrieve relevant passages using TF-IDF and cosine similarity.
* Generate context-grounded answers using Google Gemini.
* Display supporting sources for answers.
* Abstain when relevant evidence is unavailable.
* Cache repeated questions to reduce response time.
* Validate requests and handle API errors.

## Technology Stack

* Python
* Streamlit
* FastAPI
* Google Gemini API
* scikit-learn
* PyPDF
* pytest
* Render
* Streamlit Community Cloud

## Architecture

1. The user uploads a document through the Streamlit frontend.
2. FastAPI receives the document and extracts its text.
3. The extracted text is split into overlapping chunks.
4. TF-IDF and cosine similarity retrieve relevant passages.
5. Google Gemini generates an answer using the retrieved context.
6. The application displays the answer and supporting sources.
7. Repeated identical questions can reuse cached responses.

## Local Setup

### Clone the repository

```bash
git clone https://github.com/Harshith-Reddy-Sanikommu/AI-Document-Analyst.git
cd AI-Document-Analyst
```

### Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root.

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
MAX_UPLOAD_MB=10
CHUNK_SIZE=900
CHUNK_OVERLAP=150
RETRIEVAL_TOP_K=4
```

Never commit your actual API key to GitHub.

### Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

### Start the frontend

Open another terminal in the project directory.

```powershell
$env:API_URL="http://127.0.0.1:8000"
streamlit run frontend.py
```

## Testing

Run the automated tests:

```bash
python -m pytest -q
```

Recorded test result: 6 tests passed.

## Performance Evaluation

The following measurements were recorded during a live test using the sample document.

| Measurement        | Initial request | Repeated request |
| ------------------ | --------------: | ---------------: |
| Answer latency     |        2,123 ms |             0 ms |
| End-to-end request |        2,261 ms |            95 ms |
| Cache status       |            Miss |              Hit |

The repeated request reduced measured end-to-end latency by approximately 95.8% in this test. The reported answer latency of 0 ms is rounded; the complete request took 95 ms.

These measurements describe one test sequence and are not a general performance guarantee.

## Validation

* Correctly answered a question using information from the uploaded document.
* Returned a cached response for a repeated question.
* Abstained when the document did not contain the requested information.

## Limitations

* TF-IDF retrieval may miss semantically related passages.
* Scanned PDFs without extractable text may require OCR.
* Uploaded documents are stored in memory and may be lost when the backend restarts.
* The in-memory cache is not shared across backend instances.
* Free hosting services may experience cold-start delays.

## Future Improvements

* Add semantic search using embeddings.
* Support OCR for scanned documents.
* Add persistent document storage.
* Expand integration tests and retrieval-quality evaluation.
* Evaluate performance using a larger collection of documents.

## Security

API keys must be stored in environment variables or the hosting provider's secret manager. Never commit secrets to source control.

## Author

Harshith Reddy Sanikommu

GitHub: https://github.com/Harshith-Reddy-Sanikommu

LinkedIn: https://www.linkedin.com/in/harshith-reddy-sanikommu-832540341
