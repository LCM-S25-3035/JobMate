import requests
import json

# Probar la generación de preguntas desde skills
url = "http://127.0.0.1:5002/question/generate_from_skills"
data = {
    "skills": "python,flask",
    "question_count": 3
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        # Guardar la respuesta HTML para analizarla
        with open("debug_skills_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Respuesta guardada en debug_skills_response.html")
        
        # Buscar si contiene las secciones que necesitamos
        html = response.text
        print("\nAnálisis de contenido:")
        print(f"Contiene 'section-relevance': {'section-relevance' in html}")
        print(f"Contiene 'section-expected': {'section-expected' in html}")
        print(f"Contiene 'Relevancia': {'Relevancia' in html}")
        print(f"Contiene 'Respuesta esperada': {'Respuesta esperada' in html}")
        
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error en la conexión: {e}")
