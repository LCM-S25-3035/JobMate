import os
import csv
from mongo_client import create_new_collection, get_collection

def read_questions_from_csv(csv_filepath):
    with open(csv_filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames  # List of column names
        questions = [row for row in reader]  # List of dicts per row
    return headers, questions

def insert_questions_for_region(region: str, questions: list):
    collection = get_collection("onboarding_questions")
    if collection is None:
        print("Collection does not exist. Creating it...")
        create_new_collection("onboarding_questions")
        collection = get_collection("onboarding_questions")
        if collection is None:
            raise RuntimeError("Failed to create 'onboarding_questions' collection.")

    collection.update_one(
        {"region": region},
        {"$set": {"questions": questions}},
        upsert=True
    )
    print(f"Inserted/Updated questions for region: {region}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "question_dataset", "onboarding_questions.csv")
    if not csv_path:
        raise ValueError("Cannot find QUESTIONS_PATH in env.")
    
    region = "US"
    headers, questions = read_questions_from_csv(csv_path)
    print(f"Read {len(questions)} questions with headers: {headers}")

    insert_questions_for_region(region, questions)
    
# Reference: 
# PyMongo 4.13.0 documentation: https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.update_one
# OpenAI, 4o: How to fix this error? NotImplementedError: Collection objects do not implement truth value testing or bool(). Please compare with None instead: collection is not None