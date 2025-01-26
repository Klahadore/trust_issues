from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional

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

    def add_website(
        self,
        url: str,
        message: str,
        extended_message: str,
        reviews_message: Optional[str],
        reviews_extended_message: Optional[str]
    ) -> str:
        """
        Add a website with security and review information
        """
        document = {
            "url": url,
            "message": message,
            "extended_message": extended_message,
            "reviews_message": reviews_message,
            "reviews_extended_message": reviews_extended_message,
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
        """Retrieve website with all message fields"""
        try:
            document = self.collection.find_one({"url": url})
            if document:
                document = self._format_document(document)
                print(f"Retrieved document for {url}")
            else:
                print(f"No document found for {url}")
            return document
        except Exception as e:
            print(f"Retrieval operation failed: {e}")
            raise

    def _format_document(self, document: dict) -> dict:
        """Ensure consistent document structure with default values"""
        # Convert ObjectId to string
        document["_id"] = str(document["_id"])

        # Set defaults for legacy documents
        defaults = {
            "extended_message": document.get("message", ""),
            "reviews_message": document.get("message", ""),
            "reviews_extended_message": document.get("extended_message", "")
        }

        # Apply defaults for missing fields
        for field, default in defaults.items():
            document.setdefault(field, default)

        return document

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
        """Retrieve all websites with formatted messages"""
        try:
            cursor = self.collection.find()
            websites = [self._format_document(doc) for doc in cursor]
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

# Updated usage example
if __name__ == "__main__":
    db_manager = MongoDBManager()
    print(db_manager.clear_collection())
    print(db_manager.get_all_websites())
    db_manager.close()
