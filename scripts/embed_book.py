import os

from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai

load_dotenv()

# 1. Connect to MongoDB Atlas
mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

db = client["rag_book_chatbot"]
collection = db["book_chunks"]

# 2. Connect to Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(
    api_key=gemini_api_key
)

# 3. Read the book
book_id = 1

with open("data/frankenstein.txt", "r", encoding="utf-8") as file:
    book_text = file.read()


# 4. Clean Project Gutenberg content
def clean_book_text(text):

    start_marker = "START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "END OF THE PROJECT GUTENBERG EBOOK"

    start_index = text.find(start_marker)
    end_index = text.find(end_marker)

    if start_index != -1:
        text = text[start_index + len(start_marker):]

    if end_index != -1:
        text = text[:end_index]

    return text.strip()


book_text = clean_book_text(book_text)


# 5. Split the cleaned book into chunks
chunk_size = 1000
chunk_overlap = 200

chunks = []

start = 0

while start < len(book_text):

    end = start + chunk_size

    chunk = book_text[start:end]

    chunks.append(chunk)

    start = end - chunk_overlap


print("Total chunks:", len(chunks))


# 6. Create embeddings and store chunks
for i, chunk in enumerate(chunks):

    existing = collection.find_one({
        "book_id": book_id,
        "chunk_text": chunk
    })

    if existing:
        print(f"Skipped chunk {i + 1}/{len(chunks)}")
        continue

    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=chunk
    )

    embedding = response.embeddings[0].values

    document = {
        "book_id": book_id,
        "chunk_text": chunk,
        "embedding": embedding
    }

    collection.insert_one(document)

    print(f"Inserted chunk {i + 1}/{len(chunks)}")


print("Book embedding pipeline completed!")

client.close()