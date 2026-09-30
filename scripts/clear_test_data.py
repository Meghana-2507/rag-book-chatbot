import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

db = client["rag_book_chatbot"]
collection = db["book_chunks"]

result = collection.delete_many({
    "book_id": 1
})

print("Deleted documents:", result.deleted_count)

client.close()