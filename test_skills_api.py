import requests
import json

# Test directo de la API de Skills
url = "http://127.0.0.1:5002/api/generate-questions-skills"
data = {
    "skills": "python,flask",
    "level": "intermediate", 
    "question_type": "technical",
    "language": "English",
    "num_questions": "3"
}

print("🔍 Testing Skills API...")
print(f"URL: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, data=data)
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📊 Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ Request successful!")
        
        # Guardar respuesta completa
        with open("api_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("💾 Response saved to api_response.html")
        
        # Verificar si contiene preguntas
        html = response.text
        print(f"\n🔍 Analysis:")
        print(f"  - Contains 'Question:': {'Question:' in html}")
        print(f"  - Contains 'Relevance': {'Relevance' in html}")
        print(f"  - Contains 'Expected Answer': {'Expected Answer' in html}")
        print(f"  - Contains 'Generated Questions': {'Generated Questions' in html}")
        print(f"  - Contains error messages: {'Error' in html or 'error' in html}")
        
        # Buscar indicios de número de preguntas
        import re
        question_count = len(re.findall(r'Question:', html))
        print(f"  - Number of questions found: {question_count}")
        
    else:
        print(f"❌ Request failed!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"💥 Exception: {e}")
