import os
import time
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 45

st.set_page_config(page_title="AI Document Analyst", page_icon="📄", layout="wide")
st.title("AI Document Analyst")
st.caption("Upload a document, ask a question, and inspect the evidence behind the answer.")

with st.sidebar:
    st.subheader("How it works")
    st.write("1. Upload a PDF, TXT, or Markdown file.")
    st.write("2. The API extracts text and splits it into chunks.")
    st.write("3. TF-IDF retrieval selects relevant passages.")
    st.write("4. The language model answers using those passages.")
    st.info("Scanned PDFs without selectable text are not supported in this MVP.")

if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "filename" not in st.session_state:
    st.session_state.filename = None

uploaded_file = st.file_uploader("Choose a document", type=["pdf", "txt", "md"])
if uploaded_file is not None:
    if st.button("Process document", type="primary"):
        try:
            with st.spinner("Extracting and indexing document..."):
                response = requests.post(
                    f"{API_URL}/documents",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    timeout=REQUEST_TIMEOUT,
                )
            if response.ok:
                data = response.json()
                st.session_state.document_id = data["document_id"]
                st.session_state.filename = data["filename"]
                st.success(f"Processed {data['filename']} into {data['chunk_count']} chunks.")
            else:
                st.error(response.json().get("detail", "Could not process this document."))
        except requests.RequestException:
            st.error("Cannot reach the backend API. Start the API server and try again.")

if st.session_state.document_id:
    st.divider()
    st.subheader(f"Ask about: {st.session_state.filename}")
    question = st.text_area("Your question", placeholder="What are the main findings in this document?")
    if st.button("Ask question", type="primary", disabled=len(question.strip()) < 3):
        try:
            start = time.perf_counter()
            with st.spinner("Finding evidence and generating an answer..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"document_id": st.session_state.document_id, "question": question.strip()},
                    timeout=REQUEST_TIMEOUT,
                )
            if response.ok:
                data = response.json()
                st.subheader("Answer")
                st.write(data["answer"])
                col1, col2 = st.columns(2)
                col1.metric("Reported answer latency", f"{data['latency_ms']:.0f} ms")
                col2.metric("Cached answer", "Yes" if data["cached"] else "No")
                st.subheader("Supporting sources")
                if not data["sources"]:
                    st.warning("No relevant passages were found.")
                for source in data["sources"]:
                    page_label = f" · page {source['page']}" if source.get("page") else ""
                    with st.expander(f"{source['source']}{page_label} · chunk {source['chunk_id']}"):
                        st.write(source["text"])
                st.caption(f"End-to-end UI request: {(time.perf_counter() - start) * 1000:.0f} ms")
            else:
                try:
                    message = response.json().get("detail", "Question could not be answered.")
                except ValueError:
                    message = "Question could not be answered."
                st.error(message)
        except requests.Timeout:
            st.error("The request timed out. Try a shorter question or try again later.")
        except requests.RequestException:
            st.error("Cannot reach the backend API. Check that it is running.")
