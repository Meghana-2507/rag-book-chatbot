import os

from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai

load_dotenv()

# -----------------------------
# 1. Connect to MongoDB Atlas
# -----------------------------

mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

db = client["rag_book_chatbot"]
collection = db["book_chunks"]


# -----------------------------
# 2. Connect to Gemini
# -----------------------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=gemini_api_key)


# -----------------------------
# 3. Take one book chunk
# -----------------------------

book_id = 1

with open("data/frankenstein.txt", "r", encoding="utf-8") as file:
    book_text = file.read()

chunk = book_text[:1000]


# -----------------------------
# 4. Create embedding
# -----------------------------

response = gemini_client.models.embed_content(
    model="gemini-embedding-2",
    contents=chunk
)

embedding = response.embeddings[0].values


# -----------------------------
# 5. Store in MongoDB
# -----------------------------

document = {
    "book_id": book_id,
    "chunk_text": chunk,
    "embedding": embedding
}

result = collection.insert_one(document)

print("Chunk inserted successfully!")
print("MongoDB document ID:", result.inserted_id)

client.close()