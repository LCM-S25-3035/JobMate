import sys
import os
sys.path.append(os.path.abspath('.'))

from app.question.question_gen import generate_questions_from_skills

# Simular exactamente lo que haría la nueva ruta de Skills
print("=== Simulando nueva lógica de Skills route ===")

# 1. Generar datos como lo hace Skills
raw_questions_data = generate_questions_from_skills("python,flask", level="intermediate", question_type="technical", language="English", num_questions=1)

print(f"Raw data type: {type(raw_questions_data)}")
print(f"Raw data length: {len(raw_questions_data) if raw_questions_data else 0}")

# 2. Aplicar la nueva lógica condicional
if raw_questions_data and isinstance(raw_questions_data, list) and raw_questions_data[0] and 'text' in raw_questions_data[0]:
    questions_data = raw_questions_data
    print("✅ USAMOS DATOS DIRECTOS (sin build_questions_data)")
else:
    from app.main.routes import build_questions_data
    questions_data = build_questions_data(raw_questions_data) if raw_questions_data else []
    print("❌ APLICAMOS build_questions_data")

print(f"\nFinal data type: {type(questions_data)}")
print(f"Final data length: {len(questions_data) if questions_data else 0}")

if questions_data:
    q = questions_data[0]
    print(f"\nFirst question keys: {list(q.keys())}")
    print(f"Has relevance: {'relevance' in q and bool(q['relevance'])}")
    print(f"Has expected: {'expected' in q and bool(q['expected'])}")
    print(f"Relevance content: {q.get('relevance', 'NOT FOUND')[:100]}...")
    print(f"Expected content: {q.get('expected', 'NOT FOUND')[:100]}...")
