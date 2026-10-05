# RAG-Based Book Chatbot

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to ask natural-language questions about a collection of public-domain books.

The system retrieves relevant book content using **MongoDB Atlas Vector Search** and uses **Google Gemini** to generate answers based only on the retrieved book content.

## Features

* Uses 15 public-domain books from Project Gutenberg
* Stores book metadata in MySQL
* Reads book metadata from MySQL
* Loads book content from text files
* Splits book content into overlapping chunks
* Generates 384-dimensional vector embeddings using `all-MiniLM-L6-v2`
* Stores chunks and embeddings in MongoDB Atlas
* Uses MongoDB Atlas Vector Search for semantic retrieval
* Accepts natural-language questions
* Uses Google Gemini for final answer generation
* Returns the answer, evidence, book title, and author
* Provides a web interface using HTML, CSS, and JavaScript
* Handles questions unrelated to the available books
* Uses a relevance threshold to reject unrelated questions

## Architecture

```text
User Question
      ↓
HTML/CSS/JavaScript Frontend
      ↓
FastAPI Backend
      ↓
Local SentenceTransformer Embedding
(all-MiniLM-L6-v2)
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
* Sentence Transformers
* `all-MiniLM-L6-v2`
* MySQL
* MongoDB Atlas
* MongoDB Atlas Vector Search
* Google Gemini API
* HTML
* CSS
* JavaScript
* Project Gutenberg
* Git

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
│   ├── embed_books_local.py
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

## Dataset Processing

The 15 books are stored as text files in the `data/` directory.

The application:

1. Reads book metadata from MySQL.
2. Maps each book to its corresponding text file.
3. Removes unnecessary Project Gutenberg header/footer content.
4. Splits the book text into overlapping chunks.
5. Generates vector embeddings for the chunks.
6. Stores the chunks, metadata, and embeddings in MongoDB Atlas.

### Current Dataset Statistics

```text
Books: 15
Total chunks: 14,089
Chunk size: 1,000 characters
Chunk overlap: 200 characters
Embedding model: all-MiniLM-L6-v2
Embedding dimensions: 384
```

## Database Design

### MySQL

MySQL stores the metadata for each book.

Example fields:

```text
id
title
author
source
source_url
```

The application reads the book metadata from MySQL and uses the corresponding text files for processing.

### MongoDB Atlas

MongoDB Atlas stores the processed book chunks and their vector embeddings.

Each document contains information such as:

```text
book_id
title
author
source
source_url
chunk_index
chunk_text
embedding
```

MongoDB configuration:

```text
Database: rag_book_chatbot
Collection: book_chunks
Vector Index: vector_index
Similarity: cosine
Embedding dimensions: 384
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

The project uses the open-source Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The model generates **384-dimensional embeddings** for both book chunks and user questions.

These embeddings are stored in MongoDB Atlas and used by MongoDB Atlas Vector Search for semantic similarity retrieval.

### Why Local Embeddings?

The initial implementation used Google's embedding API. However, the available Gemini free-tier embedding quota was insufficient for processing the complete 15-book dataset.

Therefore, the embedding step was moved to the local `all-MiniLM-L6-v2` model.

Google Gemini is still used as the LLM for final answer generation.

This keeps the RAG architecture intact while allowing the complete dataset to be processed locally.

## RAG Workflow

When a user asks a question:

1. The frontend sends the question to the FastAPI backend.
2. The question is converted into a 384-dimensional embedding using `all-MiniLM-L6-v2`.
3. MongoDB Atlas Vector Search finds the most relevant book chunks.
4. The retrieved chunks are combined into context.
5. The question and retrieved context are sent to the Gemini LLM.
6. Gemini generates an answer using the retrieved book content.
7. The API returns the answer, evidence, book, author, and retrieval information.
8. The frontend displays the result.

The core RAG flow is:

```text
Question
   ↓
Local Embedding
   ↓
MongoDB Atlas Vector Search
   ↓
Relevant Book Chunks
   ↓
Retrieved Context
   ↓
Gemini LLM
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
  "question": "Who is Mr. Darcy?"
}
```

Example response:

```json
{
  "question": "Who is Sherlock Holmes?",
  "answer": "Sherlock Holmes is a detective...",
  "evidence": "\"My name is Sherlock Holmes. It is my business to know what other people don’t know.\"",
  "book": "The Adventures of Sherlock Holmes",
  "author": "Arthur Conan Doyle",
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

The main dependencies include:

```text
python-dotenv
pymongo
mysql-connector-python
google-genai
requests
fastapi
uvicorn
sentence-transformers
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

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
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

## Embedding the Books

The complete dataset can be processed using:

```bash
python scripts/embed_books_local.py
```

The script:

* Reads book metadata from MySQL
* Loads the corresponding book text files
* Splits the content into chunks
* Generates local embeddings using `all-MiniLM-L6-v2`
* Stores chunks and embeddings in MongoDB Atlas
* Stores book metadata along with each chunk
* Processes embeddings in batches

The completed dataset currently contains:

```text
15 books
14,089 chunks
384-dimensional embeddings
```

## Example Questions

Questions can be asked about the books in the dataset, for example:

```text
Who is Sherlock Holmes?

Who is Mr. Darcy?

Who creates the creature in Frankenstein?

What happens when Alice enters the rabbit hole?

What is the relationship between Jane Eyre and Mr. Rochester?

Who is Gatsby?

What is the central journey in The Count of Monte Cristo?
```

## Out-of-Domain Questions

The chatbot is designed specifically for questions related to the available books.

A relevance threshold is applied to the vector-search results. If a question does not appear sufficiently related to the book collection, the chatbot responds with a book-related redirection instead of generating an answer from unrelated knowledge.

For example:

```text
This chatbot is designed for book-related questions.
Please ask something about one of the available books.
```

This helps prevent unrelated questions from being answered using irrelevant retrieved content.

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

| Component                      | Status        |
| ------------------------------ | ------------- |
| Public-domain book dataset     | ✅ 15 books    |
| Book metadata in MySQL         | ✅ 15 books    |
| Book text files                | ✅ 15 books    |
| Text chunking                  | ✅ Completed   |
| Local embeddings               | ✅ Completed   |
| MongoDB Atlas                  | ✅ Working     |
| MongoDB Vector Search          | ✅ Configured  |
| Vector index                   | ✅ Ready       |
| Stored book chunks             | ✅ 14,089      |
| FastAPI backend                | ✅ Implemented |
| RAG retrieval                  | ✅ Tested      |
| Gemini LLM integration         | ✅ Working     |
| Structured responses           | ✅ Working     |
| Out-of-domain handling         | ✅ Tested      |
| Frontend                       | ✅ Implemented |
| Frontend-to-backend connection | ✅ Tested      |
| End-to-end RAG application     | ✅ Working     |

## Testing

The application has been tested with questions from multiple books, including:

* *The Adventures of Sherlock Holmes*
* *Pride and Prejudice*
* *Frankenstein; Or, The Modern Prometheus*

Out-of-domain questions have also been tested to verify that the chatbot redirects users to book-related questions.

## Conclusion

This project demonstrates a complete RAG pipeline using:

* MySQL for book metadata
* Local Sentence Transformer embeddings
* MongoDB Atlas Vector Search for semantic retrieval
* Google Gemini for answer generation
* FastAPI for the backend API
* HTML, CSS, and JavaScript for the frontend

The system retrieves relevant book content before generating an answer, helping keep responses grounded in the available book dataset.
