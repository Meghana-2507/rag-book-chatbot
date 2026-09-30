import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = connection.cursor()

query = """
INSERT INTO books (title, author, source, source_url)
VALUES (%s, %s, %s, %s)
"""

book_data = (
    "Frankenstein; Or, The Modern Prometheus",
    "Mary Wollstonecraft Shelley",
    "Project Gutenberg",
    "https://www.gutenberg.org/ebooks/84"
)

cursor.execute(query, book_data)

connection.commit()

print("Book information inserted successfully!")
print("Book ID:", cursor.lastrowid)

cursor.close()
connection.close()