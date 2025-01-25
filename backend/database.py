"""
python -m pip install "pymongo[srv]"
"""

from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
# uri = "mongodb+srv://preston281s:73lkCZHjiX6zQBzv@cluster0.vqiew.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

class MongoDBManager:
    def __init__(self):
    # Create a new client and connect to the server
        self.client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        self.db = self.client["website_manager"]
        self.collection = self.db["websites"]
        self._create_indexes()

    def _create_indexes(self):
        # Create unique index on URL to prevent duplicates
        self.collection.create_index([("url", 1)], unique=True)

    def add_website(self, url: str, message: str) -> str:
        """
        Add a website to the database with URL and message
        Returns the inserted document ID
        """
        document = {
            "url": url,
            "message": message,
            "created_at": datetime.utcnow()
        }

        try:
            result = self.collection.insert_one(document)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return None

    def website_exists(self, url: str) -> bool:
        """Check if a website exists in the database by URL"""
        return bool(self.collection.count_documents({"url": url}, limit=1))

    def get_website(self, url: str) -> dict:
        """Retrieve a website document by URL"""
        document = self.collection.find_one({"url": url})
        if document:
            document["_id"] = str(document["_id"])
        return document

    def close(self):
        """Close the MongoDB connection"""
        self.client.close()

# Usage Example
if __name__ == "__main__":
    db_manager = MongoDBManager()

    # Add a website
    website_id = db_manager.add_website(
        "https://example.com",
        "This is an example website"
    )

    if website_id:
        print(f"Added website with ID: {website_id}")
    else:
        print("Website already exists in database")

    # Check if website exists
    exists = db_manager.website_exists("https://example.com")
    print(f"Website exists: {exists}")

    # Retrieve website document
    website = db_manager.get_website("https://example.com")
    print("Website document:")
    print(website)

    db_manager.close()
