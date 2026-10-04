from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scripts.rag_engine import ask_book


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="RAG Book Chatbot API",
    description="API for asking questions about books",
    version="1.0.0"
)


# --------------------------------------------------
# CORS configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "RAG Book Chatbot API is running"
    }



# --------------------------------------------------
# Ask question
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    result = ask_book(request.question)

    return result