import os


BOOK_PATH = "data/frankenstein.txt"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
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


with open(BOOK_PATH, "r", encoding="utf-8") as file:
    text = file.read()
text = clean_book_text(text)


chunks = []

start = 0

while start < len(text):
    end = start + CHUNK_SIZE
    chunk = text[start:end]

    chunks.append(chunk)

    start = end - CHUNK_OVERLAP


print("Book chunked successfully!")
print("Total characters:", len(text))
print("Total chunks:", len(chunks))

print("\nFirst chunk:")
print(chunks[0])

print("\nSecond chunk:")
print(chunks[1])