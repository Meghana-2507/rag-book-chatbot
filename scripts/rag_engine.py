import os

from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

DB_NAME = "rag_book_chatbot"
COLLECTION_NAME = "book_chunks"

VECTOR_INDEX_NAME = "vector_index"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# MongoDB connection
# --------------------------------------------------

mongo_client = MongoClient(MONGODB_URI)

db = mongo_client[DB_NAME]

collection = db[COLLECTION_NAME]


# --------------------------------------------------
# Local embedding model
# --------------------------------------------------

print("Loading local embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

print(
    "Local embedding model loaded. "
    "Dimensions:",
    embedding_model.get_embedding_dimension()
)


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------------------------
# Create query embedding
# --------------------------------------------------

def create_query_embedding(question):

    vector = embedding_model.encode(
        question,
        normalize_embeddings=True
    )

    return vector.tolist()


# --------------------------------------------------
# MongoDB Vector Search
# --------------------------------------------------

def search_books(query_embedding, limit=5):

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "book_id": 1,
                "title": 1,
                "author": 1,
                "source": 1,
                "source_url": 1,
                "chunk_index": 1,
                "chunk_text": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    return list(
        collection.aggregate(pipeline)
    )


# --------------------------------------------------
# Build context
# --------------------------------------------------

def build_context(results):

    context = ""

    for result in results:

        context += f"""
Book: {result.get("title", "Unknown")}
Author: {result.get("author", "Unknown")}

Content:
{result["chunk_text"]}

"""

    return context


# --------------------------------------------------
# Generate answer using Gemini
# --------------------------------------------------

def generate_answer(question, context):

    prompt = f"""
You are a book question-answering assistant.

You answer questions only using the retrieved content
from the available books.

Rules:

1. Use ONLY the retrieved book content.
2. Do not use outside knowledge.
3. Do not invent or guess information.
4. Answer clearly and concisely.
5. If the retrieved content does not contain enough
   information, say:

"I couldn't find enough information about that in the retrieved book content."

6. If the question is unrelated to the available books,
   politely explain that this chatbot is designed for
   book-related questions.

Return your response in exactly this format:

Answer:
<answer>

Evidence:
<brief evidence from the retrieved content>

Book:
<book title>

Author:
<author>

Retrieved book context:
{context}

User question:
{question}
"""

    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# --------------------------------------------------
# Ask the chatbot
# --------------------------------------------------

def ask_book(question):

    query_embedding = create_query_embedding(
        question
    )

    results = search_books(
        query_embedding
    )

    if not results:

        return {
            "question": question,
            "answer": (
                "I couldn't find relevant information "
                "in the available books."
            ),
            "evidence": "",
            "book": "",
            "author": "",
            "retrieved_chunks": 0
        }

    # Check whether the question is relevant to the books
    RELEVANCE_THRESHOLD = 0.75

    top_score = results[0].get("score", 0)

    if top_score < RELEVANCE_THRESHOLD:

        return {
            "question": question,
            "answer": (
                "This chatbot is designed for book-related "
                "questions. Please ask something about one "
                "of the available books."
            ),
            "evidence": "",
            "book": "",
            "author": "",
            "retrieved_chunks": len(results)
        }

    context = build_context(
        results
    )

    answer_text = generate_answer(
        question,
        context
    )

    # Parse structured Gemini response
    answer = answer_text
    evidence = ""
    book = ""
    author = ""

    if "Answer:" in answer_text:

        answer = answer_text.split(
            "Answer:",
            1
        )[1]

    if "Evidence:" in answer:

        answer, evidence = answer.split(
            "Evidence:",
            1
        )

    if "Book:" in evidence:

        evidence, book = evidence.split(
            "Book:",
            1
        )

    if "Author:" in book:

        book, author = book.split(
            "Author:",
            1
        )

    return {
        "question": question,
        "answer": answer.strip(),
        "evidence": evidence.strip(),
        "book": book.strip(),
        "author": author.strip(),
        "retrieved_chunks": len(results)
    }