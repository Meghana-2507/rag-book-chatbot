import requests
import os

books = {
    "great_gatsby.txt": "https://www.gutenberg.org/ebooks/64317.txt.utf-8",
    "moby_dick.txt": "https://www.gutenberg.org/ebooks/2701.txt.utf-8",
    "jane_eyre.txt": "https://www.gutenberg.org/ebooks/1260.txt.utf-8",
    "wuthering_heights.txt": "https://www.gutenberg.org/ebooks/768.txt.utf-8",
    "count_of_monte_cristo.txt": "https://www.gutenberg.org/ebooks/1184.txt.utf-8"
}

data_folder = "data"

os.makedirs(data_folder, exist_ok=True)

for filename, url in books.items():

    print(f"Downloading {filename}...")

    response = requests.get(url)

    if response.status_code == 200:
        filepath = os.path.join(data_folder, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"Downloaded: {filename}")
    else:
        print(f"Failed: {filename} - Status: {response.status_code}")

print("\nDownload process completed.")