import requests
import json

# Probar la generación de preguntas desde skills después de la corrección
url = "http://127.0.0.1:5002/api/generate-questions-skills"
data = {
    "skills": "python,flask",
    "level": "intermediate",
    "question_type": "technical",
    "language": "English",
    "count": 3
}

try:
    response = requests.post(url, data=data)  # Usar data en lugar de json para form
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Preguntas generadas correctamente")
        # Verificar si es JSON o HTML
        try:
            json_response = response.json()
            print(f"JSON Response: {json_response}")
        except:
            print("HTML Response (template rendered)")
            # Guardar la respuesta HTML para ver el resultado
            with open("debug_skills_response_fixed.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Respuesta guardada en debug_skills_response_fixed.html")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error en la conexión: {e}")
