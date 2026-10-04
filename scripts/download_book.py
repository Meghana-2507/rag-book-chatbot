import requests
import os

books = [
    {
        "title": "Pride and Prejudice",
        "gutenberg_id": 1342,
        "filename": "pride_and_prejudice.txt"
    },
    {
        "title": "Alice's Adventures in Wonderland",
        "gutenberg_id": 11,
        "filename": "alice_in_wonderland.txt"
    },
    {
        "title": "The Adventures of Sherlock Holmes",
        "gutenberg_id": 1661,
        "filename": "adventures_of_sherlock_holmes.txt"
    },
    {
        "title": "Dracula",
        "gutenberg_id": 345,
        "filename": "dracula.txt"
    },
    {
        "title": "The Picture of Dorian Gray",
        "gutenberg_id": 174,
        "filename": "picture_of_dorian_gray.txt"
    },
    {
        "title": "The Time Machine",
        "gutenberg_id": 35,
        "filename": "time_machine.txt"
    },
    {
        "title": "A Tale of Two Cities",
        "gutenberg_id": 98,
        "filename": "tale_of_two_cities.txt"
    },
    {
        "title": "Little Women",
        "gutenberg_id": 37106,
        "filename": "little_women.txt"
    },
    {
        "title": "The Wonderful Wizard of Oz",
        "gutenberg_id": 55,
        "filename": "wonderful_wizard_of_oz.txt"
    }
]

os.makedirs("data", exist_ok=True)

for book in books:

    url = f"https://www.gutenberg.org/cache/epub/{book['gutenberg_id']}/pg{book['gutenberg_id']}.txt"

    file_path = os.path.join("data", book["filename"])

    # Skip if the book already exists
    if os.path.exists(file_path):
        print(f"Already exists: {book['title']}")
        continue

    print(f"Downloading: {book['title']}")

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)

            print(f"Saved to: {file_path}")
        else:
            print(
                f"Failed to download {book['title']}. "
                f"Status code: {response.status_code}"
            )

    except requests.RequestException as error:
        print(f"Error downloading {book['title']}: {error}")

print("\nDownload process completed!")