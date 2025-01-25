from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBManager:
    def __init__(self):
        # Create a new client and connect to the server
        self.client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))

        # Validate connection and database access
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            self.db = self.client["website_manager"]
            self.collection = self.db["websites"]
            self._create_indexes()
        except OperationFailure as e:
            print(f"Database connection failed: {e}")
            raise

    def _create_indexes(self):
        """Create required indexes"""
        try:
            self.collection.create_index([("url", 1)], unique=True)
            print("Database indexes verified")
        except Exception as e:
            print(f"Index creation failed: {e}")
            raise

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
            print(f"Inserted document with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            print(f"Duplicate URL detected: {url}")
            return None
        except Exception as e:
            print(f"Insert operation failed: {e}")
            raise

    def website_exists(self, url: str) -> bool:
        """Check if a website exists in the database by URL"""
        try:
            count = self.collection.count_documents({"url": url}, limit=1)
            print(f"Existence check for {url}: {bool(count)}")
            return bool(count)
        except Exception as e:
            print(f"Existence check failed: {e}")
            raise

    def get_website(self, url: str) -> dict:
        """Retrieve a website document by URL"""
        try:
            document = self.collection.find_one({"url": url})
            if document:
                document["_id"] = str(document["_id"])
                print(f"Retrieved document for {url}")
            else:
                print(f"No document found for {url}")
            return document
        except Exception as e:
            print(f"Retrieval operation failed: {e}")
            raise

    def clear_collection(self) -> int:
        """
        [DEBUG ONLY] Clear all documents from the collection
        Returns number of deleted documents
        """
        try:
            result = self.collection.delete_many({})
            print(f"Cleared {result.deleted_count} documents from collection")
            return result.deleted_count
        except Exception as e:
            print(f"Collection clearance failed: {e}")
            raise

    def get_all_websites(self) -> list[dict]:
        """
        Retrieve all website documents from the collection
        Returns list of websites with string-converted IDs
        """
        try:
            cursor = self.collection.find()
            websites = []

            for document in cursor:
                document["_id"] = str(document["_id"])
                websites.append(document)

            print(f"Retrieved {len(websites)} websites from database")
            return websites

        except Exception as e:
            print(f"Failed to retrieve websites: {e}")
            raise

    def close(self):
        """Close the MongoDB connection"""
        try:
            self.client.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage Example with debugging
if __name__ == "__main__":
    db_manager = MongoDBManager()

    try:
        # Clear existing data for clean test
        cleared = db_manager.clear_collection()
        print(f"Cleared {cleared} documents")

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

    finally:
        db_manager.close()
