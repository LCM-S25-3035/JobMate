from pymongo import MongoClient

uri = "mongodb+srv://user1:user123@jobmate.oiy0vdf.mongodb.net/?retryWrites=true&w=majority&appName=jobmate"
client = MongoClient(uri)
print(client.list_database_names())