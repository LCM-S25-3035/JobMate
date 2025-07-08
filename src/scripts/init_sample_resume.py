import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def insert_sample_resume():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB", "autoapply")
    collection_name = os.getenv("MONGO_COLLECTION", "resumes")

    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    sample_resume = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "555-1234",
        "skills": ["Python", "Machine Learning", "SQL"],
        "education": {
            "degree": "MSc Computer Science",
            "institution": "Data University",
            "year": 2023
        },
        "experience": [
            {
                "title": "Data Analyst",
                "company": "Tech Co",
                "duration": "2 years"
            }
        ]
    }

    result = collection.insert_one(sample_resume)
    print(f"✅ Sample resume inserted with ID: {result.inserted_id}")
    client.close()

if __name__ == "__main__":
    insert_sample_resume()
