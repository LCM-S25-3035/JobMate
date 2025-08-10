import sys
import os
sys.path.append(os.path.abspath('.'))

from app.question.question_gen import generate_questions_from_skills
from app.question.question_gen2 import question_generator_for_ui
from app.question.question_gen_db import generate_database_questions

# Probar qué devuelve cada generador
print("=== Probando generador de Skills ===")
try:
    skills_result = generate_questions_from_skills("python,flask", level="intermediate", question_type="technical", language="English", num_questions=2)
    print(f"Tipo: {type(skills_result)}")
    if isinstance(skills_result, list) and skills_result:
        print(f"Primer elemento: {skills_result[0]}")
        print(f"Keys del primer elemento: {skills_result[0].keys() if isinstance(skills_result[0], dict) else 'No es dict'}")
    else:
        print(f"Resultado: {skills_result}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Probando generador de Description ===")
try:
    desc_result = question_generator_for_ui("Software developer position", "Developer", "intermediate", "2-3 years", n=2)
    print(f"Tipo: {type(desc_result)}")
    if isinstance(desc_result, list) and desc_result:
        print(f"Primer elemento: {desc_result[0]}")
        print(f"Keys del primer elemento: {desc_result[0].keys() if isinstance(desc_result[0], dict) else 'No es dict'}")
    else:
        print(f"Resultado: {desc_result}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Probando generador de Database ===")
try:
    db_result = generate_database_questions("test_job", level="intermediate", question_count=2)
    print(f"Tipo: {type(db_result)}")
    print(f"Resultado: {db_result}")
except Exception as e:
    print(f"Error: {e}")
