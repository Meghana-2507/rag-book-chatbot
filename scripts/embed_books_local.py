import os
import re
import mysql.connector
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "rag_book_chatbot")

DB_NAME = "rag_book_chatbot"
COLLECTION_NAME = "book_chunks"

MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

BATCH_SIZE = 32

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data"
)


# --------------------------------------------------
# File mapping
# --------------------------------------------------

BOOK_FILES = {
    1: "frankenstein.txt",
    2: "pride_and_prejudice.txt",
    3: "alice_in_wonderland.txt",
    4: "adventures_of_sherlock_holmes.txt",
    5: "dracula.txt",
    6: "picture_of_dorian_gray.txt",
    7: "time_machine.txt",
    8: "tale_of_two_cities.txt",
    9: "little_women.txt",
    10: "wonderful_wizard_of_oz.txt",
    11: "great_gatsby.txt",
    12: "moby_dick.txt",
    13: "jane_eyre.txt",
    14: "wuthering_heights.txt",
    15: "count_of_monte_cristo.txt",
}


# --------------------------------------------------
# Connect to MySQL
# --------------------------------------------------

print("\nConnecting to MySQL...")

mysql_connection = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

mysql_cursor = mysql_connection.cursor(dictionary=True)

mysql_cursor.execute("""
    SELECT id, title, author, source, source_url
    FROM books
    ORDER BY id
""")

books = mysql_cursor.fetchall()

print(f"Found {len(books)} books in MySQL.")


# --------------------------------------------------
# Connect to MongoDB
# --------------------------------------------------

print("\nConnecting to MongoDB...")

mongo_client = MongoClient(MONGODB_URI)

mongo_db = mongo_client[DB_NAME]

collection = mongo_db[COLLECTION_NAME]

print("MongoDB connection successful.")


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

print("\nLoading embedding model...")
print(f"Model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)

test_vector = model.encode("test embedding")

print(
    f"Embedding model loaded successfully."
    f" Dimensions: {len(test_vector)}"
)


# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_gutenberg_text(text):
    """
    Remove common Project Gutenberg header/footer markers.
    """

    start_markers = [
        "*** START OF THE PROJECT GUTENBERG EBOOK",
        "*** START OF THIS PROJECT GUTENBERG EBOOK"
    ]

    end_markers = [
        "*** END OF THE PROJECT GUTENBERG EBOOK",
        "*** END OF THIS PROJECT GUTENBERG EBOOK"
    ]

    for marker in start_markers:
        index = text.find(marker)

        if index != -1:
            newline_index = text.find("\n", index)

            if newline_index != -1:
                text = text[newline_index + 1:]

            break

    for marker in end_markers:
        index = text.find(marker)

        if index != -1:
            text = text[:index]

            break

    text = re.sub(r"\r\n?", "\n", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# --------------------------------------------------
# Chunking
# --------------------------------------------------

def create_chunks(text):
    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# --------------------------------------------------
# Process each book
# --------------------------------------------------

total_chunks = 0

print("\nStarting local embedding process...\n")


for book in books:

    book_id = book["id"]

    title = book["title"]

    author = book["author"]

    filename = BOOK_FILES.get(book_id)

    if not filename:
        print(f"Skipping Book {book_id}: no file mapping.")
        continue

    file_path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(file_path):
        print(f"Skipping {title}: file not found.")
        continue

    print("=" * 70)

    print(f"Book {book_id}: {title}")

    print(f"File: {filename}")

    print("=" * 70)


    # ----------------------------------------------
    # Read book
    # ----------------------------------------------

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        text = file.read()


    # ----------------------------------------------
    # Clean text
    # ----------------------------------------------

    text = clean_gutenberg_text(text)


    # ----------------------------------------------
    # Create chunks
    # ----------------------------------------------

    chunks = create_chunks(text)

    print(f"Chunks created: {len(chunks)}")


    # ----------------------------------------------
    # Generate embeddings
    # ----------------------------------------------

    for start_index in range(
        0,
        len(chunks),
        BATCH_SIZE
    ):

        batch_chunks = chunks[
            start_index:start_index + BATCH_SIZE
        ]

        print(
            f"Embedding chunks "
            f"{start_index + 1}-"
            f"{min(start_index + BATCH_SIZE, len(chunks))}"
            f"/{len(chunks)}"
        )


        vectors = model.encode(
            batch_chunks,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True
        )


        documents = []

        for i, (chunk_text, vector) in enumerate(
            zip(batch_chunks, vectors)
        ):

            chunk_index = start_index + i

            documents.append({
                "book_id": book_id,
                "title": title,
                "author": author,
                "source": book["source"],
                "source_url": book["source_url"],
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "embedding": vector.tolist()
            })


        if documents:

            collection.insert_many(
                documents,
                ordered=False
            )


        total_chunks += len(documents)


    print(
        f"Completed: {title} "
        f"({len(chunks)} chunks)"
    )


# --------------------------------------------------
# Final summary
# --------------------------------------------------

print("\n" + "=" * 70)

print("LOCAL EMBEDDING PROCESS COMPLETED")

print("=" * 70)

print(f"Total chunks inserted: {total_chunks}")

print(
    f"MongoDB collection: "
    f"{DB_NAME}.{COLLECTION_NAME}"
)

print(
    f"Embedding model: {MODEL_NAME}"
)

print("Embedding dimensions: 384")

print("=" * 70)


mysql_cursor.close()

mysql_connection.close()

mongo_client.close()