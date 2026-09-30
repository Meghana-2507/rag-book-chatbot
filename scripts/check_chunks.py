import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)

db = client["rag_book_chatbot"]
collection = db["book_chunks"]

sample = collection.find_one(
    {"book_id": 1},
    {"_id": 0, "embedding": 1}
)

if sample and "embedding" in sample:
    embedding = sample["embedding"]

    print("Embedding exists: Yes")
    print("Embedding dimensions:", len(embedding))
else:
    print("No embedding found.")

client.close()