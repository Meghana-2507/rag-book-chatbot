# RAG-Based Book Chatbot

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to ask natural-language questions about a collection of public-domain books.

The system retrieves relevant book content using MongoDB Atlas Vector Search and uses a Large Language Model (LLM) to generate answers based only on the retrieved book content.

## Features

* Uses public-domain books from Project Gutenberg
* Stores book metadata in MySQL
* Reads book metadata from MySQL
* Loads book text from local text files
* Splits book content into overlapping chunks
* Generates vector embeddings for book chunks
* Stores chunks and embeddings in MongoDB Atlas
* Uses MongoDB Atlas Vector Search for semantic retrieval
* Accepts natural-language questions
* Uses Google Gemini for embeddings and answer generation
* Returns the answer, evidence, book title, and author
* Provides a web interface using HTML, CSS, and JavaScript
* Handles questions unrelated to the available books

## Architecture

```text
User Question
      ↓
Frontend
      ↓
FastAPI Backend
      ↓
Question Embedding
      ↓
MongoDB Atlas Vector Search
      ↓
Relevant Book Chunks
      ↓
Gemini LLM
      ↓
Structured Answer
      ↓
Frontend
```

## Technologies Used

* Python
* FastAPI
* MySQL
* MongoDB Atlas
* MongoDB Atlas Vector Search
* Google Gemini API
* HTML
* CSS
* JavaScript
* Project Gutenberg

## Project Structure

```text
rag-book-chatbot/
│
├── data/
│   ├── adventures_of_sherlock_holmes.txt
│   ├── alice_in_wonderland.txt
│   ├── count_of_monte_cristo.txt
│   ├── dracula.txt
│   ├── frankenstein.txt
│   ├── great_gatsby.txt
│   ├── jane_eyre.txt
│   ├── little_women.txt
│   ├── moby_dick.txt
│   ├── picture_of_dorian_gray.txt
│   ├── pride_and_prejudice.txt
│   ├── tale_of_two_cities.txt
│   ├── time_machine.txt
│   ├── wonderful_wizard_of_oz.txt
│   └── wuthering_heights.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── scripts/
│   ├── api.py
│   ├── check_mongodb.py
│   ├── download_book.py
│   ├── download_more_books.py
│   ├── embed_books_resume.py
│   ├── insert_book.py
│   └── rag_engine.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

> The `.env` file is intentionally not included in the repository. It contains private credentials and is excluded through `.gitignore`.

## Book Dataset

The chatbot uses 15 public-domain books from Project Gutenberg.

| #  | Book                                    | Author                      |
| -- | --------------------------------------- | --------------------------- |
| 1  | Frankenstein; Or, The Modern Prometheus | Mary Wollstonecraft Shelley |
| 2  | Pride and Prejudice                     | Jane Austen                 |
| 3  | Alice's Adventures in Wonderland        | Lewis Carroll               |
| 4  | The Adventures of Sherlock Holmes       | Arthur Conan Doyle          |
| 5  | Dracula                                 | Bram Stoker                 |
| 6  | The Picture of Dorian Gray              | Oscar Wilde                 |
| 7  | The Time Machine                        | H. G. Wells                 |
| 8  | A Tale of Two Cities                    | Charles Dickens             |
| 9  | Little Women                            | Louisa May Alcott           |
| 10 | The Wonderful Wizard of Oz              | L. Frank Baum               |
| 11 | The Great Gatsby                        | F. Scott Fitzgerald         |
| 12 | Moby-Dick; or, The Whale                | Herman Melville             |
| 13 | Jane Eyre                               | Charlotte Brontë            |
| 14 | Wuthering Heights                       | Emily Brontë                |
| 15 | The Count of Monte Cristo               | Alexandre Dumas             |

## Database Design

### MySQL

MySQL stores the metadata of each book.

Example fields:

```text
id
title
author
source
source_url
```

The application reads book metadata from MySQL and uses the corresponding text files for processing.

### MongoDB Atlas

MongoDB Atlas stores the processed book chunks and their vector embeddings.

Each document contains information such as:

```text
book_id
title
author
source
source_url
chunk_text
embedding
```

MongoDB configuration:

```text
Database: rag_book_chatbot
Collection: book_chunks
Vector Index: vector_index
```

## Text Chunking

Book content is divided into overlapping chunks before generating embeddings.

Current configuration:

```text
Chunk size: 1000 characters
Chunk overlap: 200 characters
```

The overlap helps preserve context between neighboring chunks.

## Embeddings

The project uses Google's:

```text
gemini-embedding-2
```

to convert book chunks and user questions into numerical vector representations.

The book embeddings are stored in MongoDB Atlas and used for semantic similarity search.

## RAG Workflow

When a user asks a question:

1. The frontend sends the question to the FastAPI backend.
2. The question is converted into an embedding.
3. MongoDB Atlas Vector Search finds relevant book chunks.
4. The retrieved chunks are combined into context.
5. The question and retrieved context are sent to the Gemini LLM.
6. The LLM generates an answer using the retrieved book content.
7. The API returns the answer and supporting information to the frontend.

The core RAG flow is:

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Relevant Chunks
   ↓
Context
   ↓
LLM
   ↓
Answer + Evidence
```

## API

### Health Check

```http
GET /
```

Example response:

```json
{
  "message": "RAG Book Chatbot API is running"
}
```

### Ask a Question

```http
POST /ask
```

Request:

```json
{
  "question": "What is Mr. Darcy's opinion of Elizabeth Bennet?"
}
```

The response contains fields such as:

```json
{
  "question": "...",
  "answer": "...",
  "evidence": "...",
  "book": "...",
  "author": "...",
  "retrieved_chunks": 5
}
```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Meghana-2507/rag-book-chatbot.git
cd rag-book-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```text
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_mysql_database

MONGODB_URI=your_mongodb_atlas_connection_string

GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env`, API keys, database passwords, or private connection strings to GitHub.

## Running the Application

### Start the FastAPI Backend

From the project root:

```bash
python -m uvicorn scripts.api:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### Start the Frontend

Open another terminal:

```bash
python -m http.server 5500 --directory frontend
```

Then open:

```text
http://127.0.0.1:5500
```

## Embedding Books

The project uses the resume-safe embedding script:

```bash
python scripts/embed_books_resume.py
```

The script:

* Processes Books 4–15
* Checks MongoDB for existing chunks
* Skips chunks that are already embedded
* Creates embeddings in batches
* Stores embeddings and metadata in MongoDB
* Stops safely when an API error occurs
* Can be run again later without re-embedding successfully stored chunks

## Example Questions

Questions can be asked about the books in the dataset, for example:

```text
What is the main conflict in Frankenstein?

Who is Elizabeth Bennet?

What happens to Dorian Gray?

Who is Sherlock Holmes?

What is the relationship between Jane Eyre and Mr. Rochester?

Who is Gatsby?

What is the central journey in The Count of Monte Cristo?
```

## Out-of-Domain Questions

The chatbot is designed for questions related to the available books.

For unrelated questions, the system is instructed to politely explain that it is designed for book-related questions rather than answering using unrelated outside knowledge.

## Security

Sensitive configuration is stored in environment variables.

The following should never be committed to GitHub:

```text
.env
API keys
Database passwords
Private connection strings
```

The `.gitignore` file excludes `.env` and common Python environment/cache files.

## Current Project Status

| Component                      | Status                 |
| ------------------------------ | ---------------------- |
| Book metadata in MySQL         | ✅ 15 books             |
| Book text files                | ✅ 15 books             |
| MongoDB Atlas connection       | ✅ Working              |
| MongoDB Vector Search index    | ✅ Configured           |
| FastAPI backend                | ✅ Implemented          |
| Frontend                       | ✅ Implemented          |
| Frontend-to-backend connection | ✅ Tested               |
| Book embeddings                | ⚠️ Partially completed |
| Books currently embedded       | ⚠️ Books 1–3           |
| Books awaiting embeddings      | ⏳ Books 4–15           |
| End-to-end RAG testing         | ⏳ Pending              |

### Important Note

The remaining book embeddings and end-to-end RAG testing depend on availability of the Gemini API embedding quota.

Once the embeddings are completed, the final testing will cover:

* Questions about different books
* Retrieval of relevant chunks
* Generated answers and evidence
* Book and author identification
* Unrelated/out-of-domain questions
* Frontend-to-backend end-to-end behavior
