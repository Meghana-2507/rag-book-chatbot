import requests
import os

url = "https://www.gutenberg.org/cache/epub/84/pg84.txt"

response = requests.get(url)

if response.status_code == 200:
    os.makedirs("data", exist_ok=True)

    file_path = "data/frankenstein.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(response.text)

    print("Book downloaded successfully!")
    print(f"Saved to: {file_path}")

else:
    print("Failed to download the book.")
    print("Status code:", response.status_code)