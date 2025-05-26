import os
from pymongo import MongoClient

def get_mongo_client():
    """
    This will create and return a MongoClient instance using environment variables.

    Prerequisites: Set following env vars
    - MONGODB_URI: full MongoDB connection URI
    - MONGODB_DB: database name

    Returns:
        tuple: (MongoClient instance, database name string)
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB", "autoapply")
    client = MongoClient(mongo_uri)
    return client, db_name

def create_new_collection(collection_name):
    """
    This will create a new colleciton if it does not exist. 

    Arguments: 
        collection_name (str): Name of the colleciton to create.
    """
    client, db_name = get_mongo_client()
    db = client[db_name]

    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print("Collection created successfully:", collection_name)
    else: 
        print("Collection already exists:", collection_name)

def get_collection(collection_name):
    """
    This will get a collection if it exists. 

    Arguments: 
        collection_name (str): Name of the collection to retrieve. 
    """
    client, db_name = get_mongo_client()
    db = client[db_name]

    if collection_name in db.list_collection_names():
        return db[collection_name]
    else: 
        print("Colleciton does not exist:", collection_name)
        return None