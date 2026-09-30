from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

client.admin.command("ping")

print("MongoDB Atlas connection successful!")

client.close()