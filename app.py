import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from fpdf import FPDF
import tempfile
import os
import textwrap

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoverCraft AI",
    page_icon="✉️",
    layout="centered",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0f0f0f;
    color: #e8e2d9;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
}

.hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
}

.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #e8c97e 0%, #f5e4b0 50%, #c9a84c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    margin-bottom: 0.4rem;
}

.hero p {
    color: #7a7268;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.5px;
}

.card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.6rem;
}

.stFileUploader > div {
    background: #141414 !important;
    border: 1px dashed #333 !important;
    border-radius: 10px !important;
}

.stTextArea textarea {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #e8e2d9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}

.stTextArea textarea:focus {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #e8c97e) !important;
    color: #0f0f0f !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    height: 3rem !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(201,168,76,0.3) !important;
}

.result-box {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #c9a84c;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    white-space: pre-wrap;
    font-size: 0.92rem;
    line-height: 1.85;
    color: #d4cfc8;
    font-family: 'DM Sans', sans-serif;
}

.download-section {
    background: linear-gradient(135deg, #1a1a0f, #1a160a);
    border: 1px solid #c9a84c33;
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    margin-top: 1rem;
}

.download-section p {
    color: #7a7268;
    font-size: 0.85rem;
    margin-bottom: 0.8rem;
}

div[data-testid="stDownloadButton"] button {
    background: #0f0f0f !important;
    color: #c9a84c !important;
    border: 1px solid #c9a84c !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    width: 100% !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background: #c9a84c !important;
    color: #0f0f0f !important;
}

.step-badge {
    display: inline-block;
    background: #c9a84c22;
    color: #c9a84c;
    border: 1px solid #c9a84c44;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 2px 10px;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

.stAlert {
    background: #1a1410 !important;
    border: 1px solid #c9a84c44 !important;
    color: #e8c97e !important;
    border-radius: 10px !important;
}

/* Hide default streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>CoverCraft AI</h1>
    <p>Upload your resume · Paste the job description · Download your cover letter</p>
</div>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    doc = fitz.open(tmp_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    os.unlink(tmp_path)
    return text.strip()


def generate_cover_letter(resume_text: str, jd_text: str, api_key: str) -> str:
    client = Groq(api_key=api_key)
    prompt = f"""You are an expert career coach and professional cover letter writer.

Given the candidate's resume and a job description, write a compelling, tailored cover letter.

Guidelines:
- Professional yet warm tone
- 4-5 concise paragraphs
- Opening: express genuine interest and hook
- Body: match candidate's strongest experiences to job requirements
- Body: highlight 1-2 specific projects/achievements that align with the role
- Closing: express availability and eagerness
- Do NOT include date, address blocks, or "Dear Hiring Team" header — just the body paragraphs starting from the salutation "Dear Hiring Team,"
- Do NOT use bullet points
- Do NOT add placeholder text like [Company Name]
- Keep it under 400 words

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Write the cover letter now:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=900,
    )
    return response.choices[0].message.content.strip()


def create_pdf(cover_letter_text: str, candidate_name: str = "Candidate") -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(25, 25, 25)

    # Header bar
    pdf.set_fill_color(15, 15, 15)
    pdf.rect(0, 0, 210, 28, 'F')

    # Name in header
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(220, 185, 100)
    pdf.set_xy(25, 10)
    pdf.cell(0, 10, candidate_name, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 130, 115)
    pdf.set_x(25)
    pdf.cell(0, 5, "Cover Letter", ln=True)

    # Gold divider line
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.5)
    pdf.line(25, 30, 185, 30)

    # Body
    pdf.set_y(38)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(40, 38, 35)

    # Wrap and write paragraphs
    for paragraph in cover_letter_text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # Use multi_cell for word wrap
        pdf.set_x(25)
        pdf.multi_cell(160, 6.5, paragraph)
        pdf.ln(3)

    # Footer
    pdf.set_y(-20)
    pdf.set_draw_color(201, 168, 76)
    pdf.line(25, pdf.get_y(), 185, pdf.get_y())
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(160, 150, 135)
    pdf.set_x(25)
    pdf.cell(0, 8, "Generated by CoverCraft AI  ·  Powered by LLaMA 3.3 70B", align="C")

    return pdf.output(dest='S').encode('latin-1')


# ─── API Key (from Streamlit Secrets or .env) ────────────────────────────────
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    # Fallback: load from .env for local dev
    from dotenv import load_dotenv
    import os
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "")

# ─── Step 1: Resume Upload ───────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">Step 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">📄 Upload Your Resume</div>', unsafe_allow_html=True)
resume_file = st.file_uploader(
    label="resume_upload",
    type=["pdf"],
    label_visibility="collapsed",
    help="Upload your resume as a PDF"
)
if resume_file:
    st.success(f"✓ {resume_file.name} uploaded")
st.markdown('</div>', unsafe_allow_html=True)

# ─── Step 2: Job Description ─────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="step-badge">Step 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">💼 Paste Job Description</div>', unsafe_allow_html=True)
jd_text = st.text_area(
    label="jd_input",
    placeholder="Paste the full job description here...",
    height=200,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# ─── Generate Button ─────────────────────────────────────────────────────────
generate_clicked = st.button("✨ Generate Cover Letter")

# ─── Generation Logic ─────────────────────────────────────────────────────────
if generate_clicked:
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key.")
    elif not resume_file:
        st.warning("⚠️ Please upload your resume PDF.")
    elif not jd_text.strip():
        st.warning("⚠️ Please paste a job description.")
    else:
        with st.spinner("Crafting your cover letter with LLaMA 3.3 70B..."):
            try:
                resume_text = extract_text_from_pdf(resume_file)
                # Extract candidate name (first line of resume usually)
                candidate_name = resume_text.split("\n")[0].strip() if resume_text else "Candidate"
                cover_letter = generate_cover_letter(resume_text, jd_text, api_key)
                st.session_state["cover_letter"] = cover_letter
                st.session_state["candidate_name"] = candidate_name
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ─── Display & Download ────────────────────────────────────────────────────────
if "cover_letter" in st.session_state:
    st.markdown("### ✉️ Your Cover Letter")
    st.markdown(f'<div class="result-box">{st.session_state["cover_letter"]}</div>', unsafe_allow_html=True)

    # Generate PDF
    pdf_bytes = create_pdf(
        st.session_state["cover_letter"],
        st.session_state.get("candidate_name", "Candidate")
    )

    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.markdown('<p>Your cover letter is ready to download</p>', unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Download as PDF",
        data=pdf_bytes,
        file_name="cover_letter.pdf",
        mime="application/pdf",
    )
    st.markdown('</div>', unsafe_allow_html=True)
