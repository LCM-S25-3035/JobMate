from bson.binary import Binary
from datetime import datetime, timezone
from onboarding_api.db.mongo_core import get_collection, create_new_collection

def save_resume_record(file, user_id: str, region: str) -> str:
    """
    Handles saving resumes to MongoDB (DB interaction).
    """
    collection = get_collection("resumes")
    if collection is None:
        create_new_collection("resumes")
        collection = get_collection("resumes")

    resume_bytes = Binary(file.read())

    doc = {
        "user_id": user_id,
        "region": region,
        "filename": file.name,
        "content": resume_bytes,
        "upload_date": datetime.now(timezone.utc)
    }

    result = collection.insert_one(doc)
    return str(result.inserted_id)

# Reference: 
# OpenAI 4o, first prompt: 
# now that i have resume_service, how to save the record to the collection using functions defined inside mongo_core? 

# OpenAI 4o, last prompt: 
# Getting error "AttributeError: type object 'datetime.datetime' has no attribute 'timezone'. Did you mean: 'astimezone'?"