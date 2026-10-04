from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

db = client["rag_book_chatbot"]
collection = db["book_chunks"]

print("Total chunks:", collection.count_documents({}))

print("\nChunks by book:")

pipeline = [
    {
        "$group": {
            "_id": "$book_id",
            "title": {"$first": "$title"},
            "chunks": {"$sum": 1}
        }
    },
    {
        "$sort": {"_id": 1}
    }
]

for book in collection.aggregate(pipeline):
    print(
        f"Book ID: {book['_id']} | "
        f"{book['title']} | "
        f"Chunks: {book['chunks']}"
    )

client.close()