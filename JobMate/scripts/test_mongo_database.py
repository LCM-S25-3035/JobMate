from pymongo import MongoClient


client = MongoClient("mongodb+srv://user1:user123@jobmate.oiy0vdf.mongodb.net/?retryWrites=true&w=majority&appName=jobmate")

try:
    dbs = client.list_database_names()
    print("Connected! Databases:", dbs)
except Exception as e:
    print("Connection failed:", e)