
import os
import time
import html
import requests
import streamlit as st

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

REQUEST_TIMEOUT = 45

st.set_page_config(
    page_title="AI Document Analyst",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# LOAD CSS
# --------------------------------------------------

def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as file:
            css = file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("style.css not found. Please keep it beside frontend.py.")


load_css()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "filename" not in st.session_state:
    st.session_state.filename = None

if "answer_data" not in st.session_state:
    st.session_state.answer_data = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">✦</div>
            <div>
                <div class="brand-name">DOCUMIND</div>
                <div class="brand-caption">INTELLIGENT DOCUMENTS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-heading">HOW IT WORKS</div>',
        unsafe_allow_html=True
    )

    steps = [
        ("01", "Upload document", "Choose a PDF, TXT, or Markdown file."),
        ("02", "Extract content", "The API extracts and processes the text."),
        ("03", "Find evidence", "TF-IDF retrieval identifies relevant passages."),
        ("04", "Generate answers", "The language model answers using the evidence.")
    ]

    for number, title, description in steps:
        st.markdown(
            f"""
            <div class="step-item">
                <div class="step-number">{number}</div>
                <div class="step-content">
                    <div class="step-title">{title}</div>
                    <div class="step-description">{description}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="sidebar-note">
            <div class="note-title">ⓘ GOOD TO KNOW</div>
            <p>
                Scanned PDFs without selectable text
                are not supported in this MVP.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-footer">
            DOCUMENT INTELLIGENCE<br>
            <span>POWERED BY AI</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">
            YOUR PERSONAL KNOWLEDGE ASSISTANT
        </div>

        <h1>
            Understand documents.
            <span>Discover insights.</span>
        </h1>

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
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# DOCUMENT UPLOAD SECTION
# --------------------------------------------------

st.markdown(
    """
    <div class="section-heading">
        <div class="section-kicker">STEP 01</div>
        <h2>Upload your document</h2>
        <p>Start by adding the document you want to understand.</p>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a document",
    type=["pdf", "txt", "md"],
    help="Supported formats: PDF, TXT, and Markdown."
)

if uploaded_file is not None:
    st.markdown(
        f"""
        <div class="file-preview">
            <div class="file-icon">📄</div>
            <div class="file-details">
                <div class="file-name">{html.escape(uploaded_file.name)}</div>
                <div class="file-meta">
                    {uploaded_file.size / 1024:.1f} KB · READY TO PROCESS
                </div>
            </div>
            <div class="file-status">READY</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "PROCESS DOCUMENT  →",
        type="primary",
        use_container_width=True
    ):
        try:
            with st.spinner("Extracting and indexing your document..."):
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


# --------------------------------------------------
# ACTIVE DOCUMENT
# --------------------------------------------------

if st.session_state.document_id:

    st.markdown(
        f"""
        <div class="active-document">
            <div class="active-document-icon">✓</div>
            <div>
                <div class="active-document-label">ACTIVE DOCUMENT</div>
                <div class="active-document-name">
                    {html.escape(str(st.session_state.filename))}
                </div>
            </div>
            <div class="active-document-status">INDEXED</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # --------------------------------------------------
    # QUESTION SECTION
    # --------------------------------------------------

    st.markdown(
        """
        <div class="section-heading">
            <div class="section-kicker">STEP 02</div>
            <h2>What would you like to know?</h2>
            <p>Ask a question and let AI find the relevant information.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    question = st.text_area(
        "Your question",
        placeholder=(
            "Example: What are the main findings in this document?"
        ),
        height=120,
        key="document_question"
    )

    ask_button = st.button(
        "FIND ANSWER  →",
        type="primary",
        use_container_width=True,
        disabled=len(question.strip()) < 3
    )

    if ask_button:

        try:
            start = time.perf_counter()

            with st.spinner(
                "Finding evidence and generating your answer..."
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
            st.error(
                "The request timed out. "
                "Try a shorter question or try again later."
            )

        except requests.RequestException:
            st.error(
                "Cannot reach the backend API. "
                "Check that it is running."
            )


# --------------------------------------------------
# ANSWER AND EVIDENCE
# --------------------------------------------------

if st.session_state.answer_data:

    saved = st.session_state.answer_data
    data = saved["result"]

    st.markdown("---")

    st.markdown(
        """
        <div class="section-heading">
            <div class="section-kicker">YOUR RESULTS</div>
            <h2>Analysis report</h2>
            <p>Your answer and the evidence supporting it.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Question card
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

    # Answer card
    st.markdown(
        """
        <div class="answer-heading">
            <span>✦</span> AI-GENERATED ANSWER
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="answer-card">',
        unsafe_allow_html=True
    )

    st.write(data["answer"])

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # Metrics
    st.markdown(
        '<div class="metrics-heading">ANALYSIS METRICS</div>',
        unsafe_allow_html=True
    )

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
            "Sources found",
            len(data["sources"])
        )

    # Sources
    st.markdown(
        """
        <div class="section-heading sources-heading">
            <div class="section-kicker">VERIFICATION</div>
            <h2>Supporting evidence</h2>
            <p>Explore the document passages used to generate the answer.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not data["sources"]:
        st.warning("No relevant passages were found.")

    else:
        for index, source in enumerate(data["sources"], start=1):

            page_label = (
                f" · Page {source['page']}"
                if source.get("page")
                else ""
            )

            source_title = (
                f"{index:02d}  |  {source['source']}"
                f"{page_label} · Chunk {source['chunk_id']}"
            )

            with st.expander(source_title):
                st.write(source["text"])

    st.caption(
        f"End-to-end UI request: {saved['ui_latency']:.0f} ms"
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="main-footer">
        <div class="footer-brand">DOCUMIND</div>
        <div class="footer-tagline">
            TURN INFORMATION INTO UNDERSTANDING.
        </div>
        <div class="footer-line"></div>
        <div class="footer-bottom">
            DOCUMENT INTELLIGENCE · POWERED BY AI
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
