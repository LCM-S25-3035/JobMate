import os
import json
from io import BytesIO
from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY missing in .env")

genai.configure(api_key=api_key)

def parse_resume_with_gemini(uploaded_pdf) -> dict:
    pdf_reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    if not text.strip():
        raise ValueError("❌ No text extracted from resume.")

    prompt = f"""
                You are a resume parsing expert. Extract structured JSON in this format:

                {{
                "name": "...",
                "email": "...",
                "phone": "...",
                "skills": ["...", "..."],
                "work_experience": [
                    {{
                    "company": "...",
                    "title": "...",
                    "location": "...",
                    "start_date": "...",
                    "end_date": "...",
                    "description": "..."
                    }}
                ]
                }}

                Resume Text:
                {text}
                """
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.endswith("```"):
        raw = raw[:-3]

    try:
        return json.loads(raw)
    except Exception as e:
        print("[ERROR] Gemini JSON parse failed")
        print(raw[:500])
        raise e

# Reference: 
# OpenAI 4o: given this is the previous team's python function to extract details using gemini, how can i leverage this so that i can run this like a standalone service? 