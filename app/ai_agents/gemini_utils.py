import os
import requests
from flask import current_app

def call_gemini_api(prompt, model=None):
    """
    Calls the Gemini API with the given prompt and returns the response.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    model = model or current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status_code": response.status_code}
