import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Connect to MongoDB Atlas
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)

db = client["rag_book_chatbot"]
collection = db["book_chunks"]

# Count Frankenstein chunks before deleting
book_id = 1

count = collection.count_documents({"book_id": book_id})

print(f"Frankenstein chunks found: {count}")

# Delete only Frankenstein chunks
result = collection.delete_many({"book_id": book_id})

print(f"Deleted chunks: {result.deleted_count}")

# Verify deletion
remaining = collection.count_documents({"book_id": book_id})

print(f"Remaining Frankenstein chunks: {remaining}")

client.close()