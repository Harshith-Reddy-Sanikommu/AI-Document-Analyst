
import os
import time
import html
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 45

st.set_page_config(
    page_title="AI Document Analyst",
    page_icon="📄",
    layout="wide"
)


def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        st.warning("style.css not found.")


load_css()


# SESSION STATE
if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "filename" not in st.session_state:
    st.session_state.filename = None

if "answer_data" not in st.session_state:
    st.session_state.answer_data = None


# SIDEBAR
with st.sidebar:
    st.markdown("## ✦ DOCUMIND")
    st.caption("INTELLIGENT DOCUMENTS")

    st.divider()

    st.markdown("### HOW IT WORKS")

    steps = [
        ("01", "Upload document", "Choose PDF, TXT, or Markdown."),
        ("02", "Extract content", "Extract and process document text."),
        ("03", "Find evidence", "Retrieve relevant document passages."),
        ("04", "Generate answers", "Get AI answers based on evidence.")
    ]

    for number, title, description in steps:
        st.markdown(
            f"""
            <div class="step-item">
                <div class="step-number">{number}</div>
                <div>
                    <div class="step-title">{title}</div>
                    <div class="step-description">{description}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.info(
        "Scanned PDFs without selectable text are not supported in this MVP."
    )


# HERO - NATIVE STREAMLIT COMPONENTS
st.markdown('<div class="hero-start"></div>', unsafe_allow_html=True)

st.markdown(
    "**YOUR PERSONAL KNOWLEDGE ASSISTANT**",
    help="DOCUMIND"
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            Understand documents.
            <span>Discover insights.</span>
        </div>
        <div class="hero-description">
            Turn lengthy documents into meaningful answers.
            Ask questions, explore supporting evidence,
            and find information without reading every page.
        </div>
        <div class="hero-bottom">
            ✦ AI-POWERED ANALYSIS
            &nbsp;&nbsp; ✦ EVIDENCE-BASED ANSWERS
            &nbsp;&nbsp; ✦ SMART RETRIEVAL
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# UPLOAD SECTION
st.markdown(
    """
    <div class="section-kicker">STEP 01</div>
    """,
    unsafe_allow_html=True
)

st.header("Upload your document")
st.caption("Start by adding the document you want to understand.")

uploaded_file = st.file_uploader(
    "Choose a document",
    type=["pdf", "txt", "md"],
    key="document_uploader",
    label_visibility="collapsed"
)

if uploaded_file is not None:

    st.markdown(
        f"""
        <div class="file-preview">
            <span class="file-icon">📄</span>
            <div class="file-details">
                <div class="file-name">
                    {html.escape(uploaded_file.name)}
                </div>
                <div class="file-meta">
                    {uploaded_file.size / 1024:.1f} KB · READY TO PROCESS
                </div>
            </div>
            <span class="file-status">READY</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "PROCESS DOCUMENT →",
        type="primary",
        use_container_width=True
    ):
        try:
            with st.spinner("Extracting and indexing document..."):
                response = requests.post(
                    f"{API_URL}/documents",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    },
                    timeout=REQUEST_TIMEOUT
                )

            if response.ok:
                data = response.json()

                st.session_state.document_id = data["document_id"]
                st.session_state.filename = data["filename"]
                st.session_state.answer_data = None

                st.success(
                    f"Processed {data['filename']} "
                    f"into {data['chunk_count']} chunks."
                )

            else:
                try:
                    message = response.json().get(
                        "detail",
                        "Could not process this document."
                    )
                except ValueError:
                    message = "Could not process this document."

                st.error(message)

        except requests.Timeout:
            st.error("Document processing timed out. Please try again.")

        except requests.RequestException:
            st.error(
                "Cannot reach the backend API. "
                "Start the API server and try again."
            )


# ACTIVE DOCUMENT AND QUESTION
if st.session_state.document_id:

    st.markdown(
        f"""
        <div class="active-document">
            <div class="active-check">✓</div>
            <div>
                <div class="active-label">ACTIVE DOCUMENT</div>
                <div class="active-name">
                    {html.escape(str(st.session_state.filename))}
                </div>
            </div>
            <div class="active-status">INDEXED</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<div class="section-kicker">STEP 02</div>',
        unsafe_allow_html=True
    )

    st.header("What would you like to know?")
    st.caption("Ask a question and find the relevant information.")

    question = st.text_area(
        "Your question",
        placeholder="What are the main findings in this document?",
        height=120
    )

    if st.button(
        "FIND ANSWER →",
        type="primary",
        use_container_width=True,
        disabled=len(question.strip()) < 3
    ):

        try:
            start = time.perf_counter()

            with st.spinner("Finding evidence and generating an answer..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "document_id": st.session_state.document_id,
                        "question": question.strip()
                    },
                    timeout=REQUEST_TIMEOUT
                )

            if response.ok:
                data = response.json()

                st.session_state.answer_data = {
                    "question": question.strip(),
                    "result": data,
                    "ui_latency": (
                        time.perf_counter() - start
                    ) * 1000
                }

            else:
                try:
                    message = response.json().get(
                        "detail",
                        "Question could not be answered."
                    )
                except ValueError:
                    message = "Question could not be answered."

                st.error(message)

        except requests.Timeout:
            st.error("The request timed out. Please try again.")

        except requests.RequestException:
            st.error("Cannot reach the backend API.")


# RESULTS
if st.session_state.answer_data:

    saved = st.session_state.answer_data
    data = saved["result"]

    st.divider()

    st.markdown(
        '<div class="section-kicker">YOUR RESULTS</div>',
        unsafe_allow_html=True
    )

    st.header("Analysis report")
    st.caption("Your answer and the evidence supporting it.")

    st.markdown(
        f"""
        <div class="question-card">
            <div class="result-label">YOUR QUESTION</div>
            <div class="question-text">
                {html.escape(saved["question"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### ✦ AI-GENERATED ANSWER")

    st.markdown('<div class="answer-card">', unsafe_allow_html=True)
    st.write(data["answer"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### ANALYSIS METRICS")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Answer latency", f"{data['latency_ms']:.0f} ms")

    with col2:
        st.metric("Cached answer", "Yes" if data["cached"] else "No")

    with col3:
        st.metric("Sources found", len(data["sources"]))

    st.markdown("---")
    st.markdown("### Supporting evidence")

    if not data["sources"]:
        st.warning("No relevant passages were found.")

    for index, source in enumerate(data["sources"], start=1):

        page_label = (
            f" · Page {source['page']}"
            if source.get("page")
            else ""
        )

        title = (
            f"{index:02d} | {source['source']}"
            f"{page_label} · Chunk {source['chunk_id']}"
        )

        with st.expander(title):
            st.write(source["text"])

    st.caption(
        f"End-to-end UI request: {saved['ui_latency']:.0f} ms"
    )


# FOOTER
st.markdown(
    """
    <div class="main-footer">
        <div class="footer-brand">DOCUMIND</div>
        <div class="footer-tagline">
            TURN INFORMATION INTO UNDERSTANDING.
        </div>
        <div class="footer-bottom">
            DOCUMENT INTELLIGENCE · POWERED BY AI
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
