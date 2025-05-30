from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Use your existing URI
# MONGO_URI = "mongodb://airflow:airflow@localhost:27017/autoapply?authSource=admin"

MONGO_URI = "mongodb://localhost:27017/"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Trigger a call to test the connection
    print("✅ MongoDB connection successful!")

    # Optionally list databases
    print("📂 Databases:", client.list_database_names())
    
    # Optionally list collections in your DB
    db = client["autoapply"]
    print("📁 Collections in 'autoapply':", db.list_collection_names())

except ConnectionFailure as e:
    print("❌ MongoDB connection failed:", e)