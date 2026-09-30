import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai

load_dotenv()

# MongoDB connection
mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

db = client["rag_book_chatbot"]
collection = db["book_chunks"]

# Gemini connection
gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=gemini_api_key)

print("MongoDB and Gemini connections initialized successfully!")
# Test question
question = input("\nAsk a question about the book: ")

# Create embedding for the question
response = gemini_client.models.embed_content(
    model="gemini-embedding-2",
    contents=question
)

query_embedding = response.embeddings[0].values

print("Question embedding created successfully!")
print("Embedding dimensions:", len(query_embedding))
# Search for relevant book chunks
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 10,
            "limit": 3
        }
    }
]

results = list(collection.aggregate(pipeline))

print("\nRelevant book chunks:\n")

for result in results:
    print("----------------------------------------")
    print(result["chunk_text"])
    print("----------------------------------------")
    # Build context from retrieved book chunks
context = ""

for result in results:
    context += result["chunk_text"] + "\n\n"

print("\nContext created successfully!")
# Generate an answer using Gemini
prompt = f"""
You are a book question-answering assistant.

Your job is to answer questions using ONLY the provided book context.

Rules:
1. Use only information supported by the book context.
2. Do not use your general knowledge or outside information.
3. If the context contains enough information to answer the question,
   provide a clear and concise answer.
4. If the context does not contain enough information to answer the question,
   say exactly:
   "I couldn't find enough information about that in the book."
5. Do not invent or guess facts.
6. Do not answer unrelated questions using general knowledge.
7. Always return the answer in the following format:

Answer:
<answer based only on the book context>

Evidence:
<brief explanation based only on the retrieved context>

Book:
Frankenstein; Or, The Modern Prometheus

8. If the context is insufficient, use the required "I couldn't find enough
   information..." response and do not invent evidence.

Book context:
{context}

User question:
{question}
"""


# Generate answer with retry handling
max_retries = 3

for attempt in range(max_retries):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        print("\nAnswer:")
        print(response.text)
        break

    except Exception as error:
        print(f"\nGemini request failed (attempt {attempt + 1}/{max_retries})")

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print("Gemini request failed after all retries.")
            print(error)