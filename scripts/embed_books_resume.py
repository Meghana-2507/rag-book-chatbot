import os
import mysql.connector

from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai
from google.genai import types

load_dotenv()

# -----------------------------
# MySQL connection
# -----------------------------
mysql_connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

mysql_cursor = mysql_connection.cursor(dictionary=True)

# -----------------------------
# MongoDB connection
# -----------------------------
mongodb_uri = os.getenv("MONGODB_URI")

mongo_client = MongoClient(mongodb_uri)
mongo_db = mongo_client["rag_book_chatbot"]
collection = mongo_db["book_chunks"]

# -----------------------------
# Gemini client
# -----------------------------
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Book files
# -----------------------------
book_files = {
    4: "data/adventures_of_sherlock_holmes.txt",
    5: "data/dracula.txt",
    6: "data/picture_of_dorian_gray.txt",
    7: "data/time_machine.txt",
    8: "data/tale_of_two_cities.txt",
    9: "data/little_women.txt",
    10: "data/wonderful_wizard_of_oz.txt",
    11: "data/great_gatsby.txt",
    12: "data/moby_dick.txt",
    13: "data/jane_eyre.txt",
    14: "data/wuthering_heights.txt",
    15: "data/count_of_monte_cristo.txt"
}

# -----------------------------
# Settings
# -----------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 50


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


def create_chunks(book_text):
    chunks = []

    start = 0

    while start < len(book_text):
        end = start + CHUNK_SIZE

        chunk = book_text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start = end - CHUNK_OVERLAP

    return chunks


# -----------------------------
# Get Books 4–15 from MySQL
# -----------------------------
mysql_cursor.execute("""
    SELECT id, title, author, source, source_url
    FROM books
    WHERE id BETWEEN 4 AND 15
    ORDER BY id
""")

books = mysql_cursor.fetchall()

print("=" * 60)
print("RESUME-SAFE BOOK EMBEDDING")
print("=" * 60)
print(f"Books found: {len(books)}")
print()


overall_failed = False


# -----------------------------
# Process each book
# -----------------------------
for book in books:

    book_id = book["id"]
    title = book["title"]
    author = book["author"]

    print("=" * 60)
    print(f"Book ID : {book_id}")
    print(f"Title   : {title}")
    print(f"Author  : {author}")
    print("=" * 60)

    file_path = book_files.get(book_id)

    if not file_path:
        print("No file mapping found.")
        overall_failed = True
        continue

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        overall_failed = True
        continue

    # -------------------------
    # Read book
    # -------------------------
    with open(file_path, "r", encoding="utf-8") as file:
        book_text = file.read()

    book_text = clean_book_text(book_text)

    print(f"Characters: {len(book_text):,}")

    # -------------------------
    # Create chunks
    # -------------------------
    chunks = create_chunks(book_text)

    print(f"Total chunks: {len(chunks):,}")

    # -------------------------
    # Check existing chunks
    # -------------------------
    chunks_to_embed = []

    for chunk in chunks:

        existing = collection.find_one({
            "book_id": book_id,
            "chunk_text": chunk
        })

        if not existing:
            chunks_to_embed.append(chunk)

    print(
        f"Chunks needing embeddings: "
        f"{len(chunks_to_embed):,}"
    )

    # Nothing left to do
    if not chunks_to_embed:
        print("Nothing to embed for this book.")
        print()
        continue

    inserted = 0
    book_failed = False

    # -------------------------
    # Batch embedding
    # -------------------------
    for start_index in range(
        0,
        len(chunks_to_embed),
        BATCH_SIZE
    ):

        batch_chunks = chunks_to_embed[
            start_index:
            start_index + BATCH_SIZE
        ]

        batch_start = start_index + 1
        batch_end = start_index + len(batch_chunks)

        print()
        print(
            f"Embedding chunks "
            f"{batch_start}-{batch_end} "
            f"of {len(chunks_to_embed)}"
        )

        try:

            contents = [
                types.Content(
                    parts=[
                        types.Part.from_text(
                            text=chunk
                        )
                    ]
                )
                for chunk in batch_chunks
            ]

            response = gemini_client.models.embed_content(
                model="gemini-embedding-2",
                contents=contents
            )

            embeddings = response.embeddings

            if len(embeddings) != len(batch_chunks):

                print(
                    "ERROR: Number of embeddings "
                    "does not match number of chunks."
                )

                book_failed = True
                overall_failed = True
                break

            documents = []

            for chunk, embedding in zip(
                batch_chunks,
                embeddings
            ):

                document = {
                    "book_id": book_id,
                    "title": title,
                    "author": author,
                    "source": book["source"],
                    "source_url": book["source_url"],
                    "chunk_text": chunk,
                    "embedding": embedding.values
                }

                documents.append(document)

            if documents:
                collection.insert_many(documents)

            inserted += len(documents)

            print(
                f"Inserted this batch: {len(documents)}"
            )

            print(
                f"Total inserted for this book: "
                f"{inserted}"
            )

        except Exception as error:

            print()
            print("ERROR while creating embeddings:")
            print(error)

            print()
            print(
                "Stopping this book."
            )

            print(
                "Already inserted batches are safe."
            )

            book_failed = True
            overall_failed = True

            break

    print()
    print("-" * 60)

    if book_failed:
        print(
            f"Book stopped with an error: {title}"
        )
    else:
        print(
            f"Book successfully processed: {title}"
        )

    print(f"Inserted in this run: {inserted}")
    print("-" * 60)
    print()


# -----------------------------
# Close connections
# -----------------------------
mysql_cursor.close()
mysql_connection.close()
mongo_client.close()


# -----------------------------
# Final status
# -----------------------------
print("=" * 60)

if overall_failed:
    print("EMBEDDING PROCESS FINISHED WITH ERRORS")
    print("Run the same script again after the issue is resolved.")
else:
    print("ALL REQUESTED BOOKS PROCESSED SUCCESSFULLY")

print("=" * 60)