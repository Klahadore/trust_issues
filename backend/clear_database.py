# clear_database.py
from database import MongoDBManager
from dotenv import load_dotenv
import os

def clear_database():
    load_dotenv()
    try:
        with MongoDBManager() as db:
            count = db.clear_collection()
            print(f"Successfully cleared {count} documents from the database")
    except Exception as e:
        print(f"Error clearing database: {str(e)}")

if __name__ == "__main__":
    clear_database()
