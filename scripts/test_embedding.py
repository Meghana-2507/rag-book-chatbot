
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

text = "Victor Frankenstein created the creature."

response = client.models.embed_content(
    model="gemini-embedding-2",
    contents=text
)

embedding = response.embeddings[0].values

print("Embedding created successfully!")
print("Number of dimensions:", len(embedding))
print("First 10 values:", embedding[:10])