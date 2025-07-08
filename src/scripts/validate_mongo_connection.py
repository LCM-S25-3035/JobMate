# scripts/validate_mongo_connection.py

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_mongo_connection(target_collection: str = "resumes"):
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB", "autoapply")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ MongoDB connection successful.")

        db = client[db_name]
        if target_collection in db.list_collection_names():
            print(f"✅ Collection '{target_collection}' exists in '{db_name}' database.")
        else:
            print(f"⚠️ Collection '{target_collection}' not found in '{db_name}' database.")
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    finally:
        client.close()

# Use this for Airflow DAG PythonOperator
def validate_jobs_collection():
    validate_mongo_connection("jobs")

# Script entry point
if __name__ == "__main__":
    collection = os.getenv("MONGO_COLLECTION", "resumes")
    validate_mongo_connection(collection)
