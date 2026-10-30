
import os
import time
import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

REQUEST_TIMEOUT = 45


# PAGE CONFIGURATION
st.set_page_config(
    page_title="AI Document Analyst",
    page_icon="📄",
    layout="wide"
)


# LOAD CSS
def load_css():
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


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

    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">D.</div>
        <div>
            <div class="brand-title">DOC ANALYST</div>
            <div class="brand-subtitle">INTELLIGENCE WORKSPACE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-heading">HOW IT WORKS</div>',
        unsafe_allow_html=True
    )

    steps = [
        ("01", "Upload document", "Select PDF, TXT or Markdown."),
        ("02", "Extract content", "Extract and divide document text."),
        ("03", "Find evidence", "Retrieve relevant passages using TF-IDF."),
        ("04", "Generate answer", "Get an AI response grounded in evidence.")
    ]

    for number, title, description in steps:

        st.markdown(f"""
        <div class="workflow-step">
            <div class="step-number">{number}</div>
            <div>
                <div class="step-title">{title}</div>
                <div class="step-description">{description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-note">
        <b>DOCUMENT NOTE</b>
        <p>
            Scanned PDFs without selectable text are
            not supported in this MVP.
        </p>
    </div>
    """, unsafe_allow_html=True)


# HERO SECTION
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">
        YOUR PERSONAL KNOWLEDGE ASSISTANT
    </div>

    <h1>Understand documents.<br>
    <span>Discover insights.</span></h1>

    <p>
        Turn lengthy documents into meaningful answers.
        Ask questions, explore supporting evidence,
        and find information without reading every page.
    </p>

    <div class="hero-bottom">
        <span>✦ AI-POWERED ANALYSIS</span>
        <span>✦ EVIDENCE-BASED ANSWERS</span>
        <span>✦ SMART RETRIEVAL</span>
    </div>
</div>
""", unsafe_allow_html=True)


# DOCUMENT UPLOAD
st.markdown("""
<div class="section-heading">
    <div class="section-number">01 / DOCUMENT</div>
    <h2>Bring your document</h2>
    <p>
        Upload a document to extract its content
        and prepare it for intelligent analysis.
    </p>
</div>
""", unsafe_allow_html=True)


upload_col, details_col = st.columns([1.5, 1])


with upload_col:

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "txt", "md"],
        help="Supported formats: PDF, TXT and Markdown"
    )


with details_col:

    st.markdown("""
    <div class="format-card">
        <div class="format-icon">PDF</div>
        <div class="format-title">Supported formats</div>
        <div class="format-list">
            PDF Documents<br>
            Text Files (TXT)<br>
            Markdown Files (MD)
        </div>
        <div class="format-footer">
            DOCUMENT INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)


if uploaded_file is not None:

    st.markdown(
        f'<div class="selected-file">✓ Selected: {uploaded_file.name}</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "PROCESS DOCUMENT  →",
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
                    f"Successfully processed {data['filename']} "
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


# QUESTION SECTION
if st.session_state.document_id:

    st.markdown("---")

    st.markdown("""
    <div class="section-heading">
        <div class="section-number">02 / ASK YOUR DOCUMENT</div>
        <h2>What would you like to know?</h2>
        <p>
            Ask a question and let AI find the relevant
            information from your document.
        </p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown(f"""
    <div class="active-document">
        <span class="document-indicator">●</span>
        ACTIVE DOCUMENT
        <strong>{st.session_state.filename}</strong>
    </div>
    """, unsafe_allow_html=True)


    question = st.text_area(
        "Your question",
        placeholder="What are the main findings in this document?",
        height=130
    )


    if st.button(
        "FIND ANSWER  →",
        type="primary",
        use_container_width=True,
        disabled=len(question.strip()) < 3
    ):

        try:

            start = time.perf_counter()

            with st.spinner(
                "Finding evidence and generating an answer..."
            ):

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
                    "data": data,
                    "question": question.strip(),
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

            st.error(
                "The request timed out. "
                "Try a shorter question or try again later."
            )

        except requests.RequestException:

            st.error(
                "Cannot reach the backend API. Check that it is running."
            )


# DISPLAY ANSWER
if st.session_state.answer_data:

    result = st.session_state.answer_data
    data = result["data"]

    st.markdown("""
    <div class="section-heading">
        <div class="section-number">03 / ANALYSIS RESULTS</div>
        <h2>Your document insights</h2>
        <p>Here is what we discovered from your document.</p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown(f"""
    <div class="question-card">
        <div class="question-label">YOUR QUESTION</div>
        <div class="question-text">{result["question"]}</div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("""
    <div class="answer-card">
        <div class="answer-label">✦ AI GENERATED ANSWER</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="answer-content">{data["answer"]}</div>',
        unsafe_allow_html=True
    )


    # METRICS
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Answer latency",
            f"{data['latency_ms']:.0f} ms"
        )

    with col2:
        st.metric(
            "Cached answer",
            "Yes" if data["cached"] else "No"
        )

    with col3:
        st.metric(
            "Supporting passages",
            len(data["sources"])
        )


    # SOURCES
    st.markdown("""
    <div class="section-heading">
        <div class="section-number">04 / EVIDENCE</div>
        <h2>Supporting sources</h2>
        <p>Explore the passages used to generate the answer.</p>
    </div>
    """, unsafe_allow_html=True)


    if not data["sources"]:

        st.warning("No relevant passages were found.")

    else:

        for index, source in enumerate(data["sources"], 1):

            page_label = (
                f" · Page {source['page']}"
                if source.get("page")
                else ""
            )

            with st.expander(
                f"PASSAGE {index:02d}  ·  {source['source']}"
                f"{page_label}  ·  CHUNK {source['chunk_id']}"
            ):

                st.markdown(
                    f'<div class="source-text">{source["text"]}</div>',
                    unsafe_allow_html=True
                )


    st.caption(
        f"End-to-end UI request: {result['ui_latency']:.0f} ms"
    )


# FOOTER
st.markdown("""
<div class="footer">
    DOCUMENT INTELLIGENCE
    <span> · </span>
    POWERED BY AI
</div>
""", unsafe_allow_html=True)
