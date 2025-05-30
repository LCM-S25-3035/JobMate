from onboarding_api.db.mongo_core import create_new_collection, get_collection

def insert_questions(questions: list):
    collection = get_collection("onboarding_questions")
    if collection is None:
        print("Collection does not exist. Creating it...")
        create_new_collection("onboarding_questions")
        collection = get_collection("onboarding_questions")

    count = 0
    for q in questions:
        collection.update_one(
            {"question_id": q["question_id"]},
            {"$set": q},
            upsert=True
        )
        count += 1
    print(f"{count} questions inserted.")

# Reference: 
# PyMongo 4.13.0 documentation: https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.update_one
