import sys
import os
sys.path.append(os.path.abspath('.'))

from app.question.question_gen import generate_questions_from_skills
from app.main.routes import build_questions_data

# Probar qué pasa con build_questions_data
print("=== Datos originales del generador ===")
original_data = generate_questions_from_skills("python,flask", level="intermediate", question_type="technical", language="English", num_questions=1)
print(f"Original: {original_data[0] if original_data else 'None'}")

print("\n=== Después de build_questions_data ===")
processed_data = build_questions_data(original_data)
print(f"Processed: {processed_data[0] if processed_data else 'None'}")

print("\n=== Comparación de claves ===")
if original_data and processed_data:
    print(f"Original keys: {original_data[0].keys()}")
    print(f"Processed keys: {processed_data[0].keys()}")
    
    print(f"\nOriginal relevance: {original_data[0].get('relevance', 'NOT FOUND')}")
    print(f"Processed relevance: {processed_data[0].get('relevance', 'NOT FOUND')}")
    
    print(f"\nOriginal expected: {original_data[0].get('expected', 'NOT FOUND')}")
    print(f"Processed expected: {processed_data[0].get('expected', 'NOT FOUND')}")
