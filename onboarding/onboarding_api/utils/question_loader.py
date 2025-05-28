import csv
import ast

def read_questions_from_csv(csv_filepath):
    questions = []
    with open(csv_filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                question = {
                    "question_id": row["question_id"].strip(),
                    "question_text": row["question_text"].strip(),
                    "type": row["type"].strip(),
                    "required": row["required"].strip().upper(),
                    "options": ast.literal_eval(row["options"]) if row.get("options") else [],
                    "step": int(row["step"]),
                    "region": ast.literal_eval(row["region"]) if row.get("region") else []
                }
                questions.append(question)
            except Exception as e:
                print("[ERROR] Skipping row due to error:", e)
    return questions

# Reference:
# OpenAI, 4o: How to fix this error? NotImplementedError: Collection objects do not implement truth value testing or bool(). Please compare with None instead: collection is not None
# OpenAI, 4o: Getting error -> UnicodeDecodeError: 'utf-8' codec can't decode byte 0x96 in position 691: invalid start byte