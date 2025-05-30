import csv
import ast
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from onboarding_api.db.mongo_core import create_new_collection, get_collection

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

def insert_questions_for_region(questions: list):
    collection = get_collection("onboarding_questions")
    count=0
    if collection is None:
        print("Collection does not exist. Creating it...")
        create_new_collection("onboarding_questions")
        collection = get_collection("onboarding_questions")
        if collection is None:
            raise RuntimeError("Failed to create 'onboarding_questions' collection.")
    
    for q in questions:
        collection.update_one(
            {"question_id": q["question_id"]},
            {"$set": q},
            upsert=True
        )
        count += 1 
    print(f"{count} questions inserted.")

def __index__(self):
    return self.__int__()

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "question_dataset", "onboarding_questions.csv")
    if not csv_path:
        raise ValueError("Cannot find QUESTIONS_PATH in env.")
    
    questions = read_questions_from_csv(csv_path)
    insert_questions_for_region(questions)

# Reference: 
# OpenAI 4o, first prompt: 
# how can i make sure that the questions are loaded for one-time setup. i will be using mong_core from db folder get and collect collection. 

# OpenAI 4o, last prompt: 
# why am i getting this error? "ModuleNotFoundError: No module named 'onboarding_api'" the file is already under 