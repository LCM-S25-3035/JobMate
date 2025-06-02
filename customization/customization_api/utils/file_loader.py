import json
from docx import Document

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_template_text(docx_path):
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs)
