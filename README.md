# RAG Book Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions from a book using Gemini embeddings, MongoDB Atlas Vector Search, and Gemini for answer generation.

## Project Overview

This project implements a basic RAG pipeline using *Frankenstein; Or, The Modern Prometheus* by Mary Wollstonecraft Shelley.

The system:

1. Loads and cleans the book text.
2. Splits the book into overlapping text chunks.
3. Generates embeddings for the chunks using Gemini.
4. Stores the chunks and embeddings in MongoDB.
5. Converts a user's question into an embedding.
6. Uses MongoDB Atlas Vector Search to retrieve relevant book chunks.
7. Builds context from the retrieved chunks.
8. Sends the question and retrieved context to Gemini.
9. Generates an answer based only on the retrieved book context.

## Current Implementation

The following components have been implemented:

* Book text loading and cleaning
* Text chunking with overlap
* Gemini embedding generation
* MongoDB storage of book chunks and embeddings
* MongoDB Atlas Vector Search
* Question embedding generation
* Retrieval of relevant book chunks
* Context construction
* Gemini-based answer generation
* Retry handling for Gemini requests
* MySQL book metadata insertion
* Basic testing scripts for Gemini, MongoDB, embeddings, and vector search

## Project Structure

```text
rag-book-chatbot/
│
├── data/
│   └── frankenstein.txt
│
├── scripts/
│   ├── download_book.py
│   ├── insert_book.py
│   ├── chunk_book.py
│   ├── embed_book.py
│   ├── rag_chatbot.py
│   ├── check_chunks.py
│   ├── clear_book_chunks.py
│   ├── clear_test_data.py
│   ├── test_embedding.py
│   ├── test_gemini.py
│   ├── test_mongodb.py
│   ├── test_mongodb_insert.py
│   └── test_vector_search.py
│
├── test_mysql.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies Used

* Python
* Gemini API
* MongoDB Atlas
* MongoDB Atlas Vector Search
* MySQL
* HTML/CSS/JavaScript can be added later for a user-facing interface

## Environment Variables

Create a `.env` file locally with the required credentials:

```text
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_connection_string

MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_mysql_database
```

Do not commit the `.env` file or expose API keys and database credentials.

## Running the RAG Chatbot

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Make sure MongoDB Atlas is configured with the required database, collection, and vector search index.

Then run:

```bash
python scripts/rag_chatbot.py
```

Enter a question about *Frankenstein* when prompted.

The application retrieves relevant book chunks using vector search and uses Gemini to generate an answer from the retrieved context.

## Current Status

The core RAG pipeline has been implemented and tested through the individual processing, embedding, vector search, and chatbot components.

Further work can include improving the chatbot interface, refining retrieval quality, adding more books, and integrating the complete application into a user-facing frontend.
