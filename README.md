# CoverCraft AI ✉️

An AI-powered cover letter generator built with Streamlit, Groq API (LLaMA 3.3 70B), and PDF export.

## Features
- 📄 Upload your resume as PDF — text is auto-extracted
- 💼 Paste any job description
- ✨ AI generates a tailored, professional cover letter
- ⬇️ Download the result as a formatted PDF

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Groq API Key
Sign up free at [console.groq.com](https://console.groq.com) and create an API key.

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Use it
1. Enter your Groq API key in the app
2. Upload your resume (PDF)
3. Paste the job description
4. Click **Generate Cover Letter**
5. Download the PDF!

## Tech Stack
- **Frontend**: Streamlit
- **AI Model**: LLaMA 3.3 70B via Groq API
- **PDF Parsing**: PyMuPDF (fitz)
- **PDF Generation**: fpdf2
