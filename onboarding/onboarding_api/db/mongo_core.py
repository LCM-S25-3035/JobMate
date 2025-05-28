import os
from pymongo import MongoClient

def get_mongo_client():
    mongo_uri = "mongodb://airflow:airflow@localhost:27017/?authSource=admin"
    db_name = os.getenv("MONGO_DB", "autoapply")
    client = MongoClient(mongo_uri)
    return client, db_name

def create_new_collection(collection_name):
    client, db_name = get_mongo_client()
    db = client[db_name]

    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print("Collection created successfully:", collection_name)
    else: 
        print("Collection already exists:", collection_name)

def get_collection(collection_name):
    client, db_name = get_mongo_client()
    db = client[db_name]

    if collection_name in db.list_collection_names():
        return db[collection_name]
    else: 
        print("Colleciton does not exist:", collection_name)
        return None