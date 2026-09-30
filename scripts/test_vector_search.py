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
# 3. User's question
# -----------------------------

question = "What is Frankenstein?"


# -----------------------------
# 4. Create question embedding
# -----------------------------

response = gemini_client.models.embed_content(
    model="gemini-embedding-2",
    contents=question
)

query_embedding = response.embeddings[0].values


# -----------------------------
# 5. Perform vector search
# -----------------------------

pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 50,
            "limit": 5
        }
    }
]


results = collection.aggregate(pipeline)


# -----------------------------
# 6. Display results
# -----------------------------

print("\nRelevant book chunks:\n")

for result in results:
    print("----------------------------------------")
    print(result["chunk_text"][:500])
    print("----------------------------------------")


client.close()