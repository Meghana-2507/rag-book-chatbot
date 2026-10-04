import os
from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai

load_dotenv()


# --------------------------------------------------
# Connections
# --------------------------------------------------

mongodb_uri = os.getenv("MONGODB_URI")

mongo_client = MongoClient(mongodb_uri)

db = mongo_client["rag_book_chatbot"]
collection = db["book_chunks"]

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------------------------
# Create question embedding
# --------------------------------------------------

def create_query_embedding(question):

    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=question
    )

    return response.embeddings[0].values


# --------------------------------------------------
# Search relevant book chunks
# --------------------------------------------------

def search_books(query_embedding, limit=5):

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 20,
                "limit": limit
            }
        }
    ]

    return list(collection.aggregate(pipeline))


# --------------------------------------------------
# Build context from retrieved chunks
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
# Generate answer
# --------------------------------------------------

def generate_answer(question, context):
    prompt = f"""
You are a book question-answering assistant.

Answer the user's question using ONLY the retrieved book content.

Rules:

1. Do not use outside knowledge.
2. Do not invent or guess information.
3. If the context contains enough information, answer clearly.
4. Use the book content to provide evidence.
5. If the context does not contain enough information, say:
"I couldn't find enough information about that in the retrieved book content."
6. If the question is unrelated to the available books, politely explain
that this chatbot is designed for book-related questions.

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
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text
# --------------------------------------------------
# Complete RAG pipeline
# --------------------------------------------------

def ask_book(question):
    query_embedding = create_query_embedding(question)

    results = search_books(query_embedding)

    if not results:
        return {
            "question": question,
            "answer": "I couldn't find relevant information in the available books.",
            "evidence": "",
            "book": "",
            "author": "",
            "retrieved_chunks": 0
        }

    context = build_context(results)

    answer_text = generate_answer(question, context)

    answer = answer_text
    evidence = ""
    book = ""
    author = ""

    if "Answer:" in answer_text:
        answer = answer_text.split("Answer:", 1)[1]

    if "Evidence:" in answer:
        answer, evidence = answer.split("Evidence:", 1)

    if "Book:" in evidence:
        evidence, book = evidence.split("Book:", 1)

    if "Author:" in book:
        book, author = book.split("Author:", 1)

    return {
        "question": question,
        "answer": answer.strip(),
        "evidence": evidence.strip(),
        "book": book.strip(),
        "author": author.strip(),
        "retrieved_chunks": len(results)
    }