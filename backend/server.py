from typing import Dict, Union
from fastapi import FastAPI, HTTPException, status
from urllib.parse import urlsplit
from database import MongoDBManager
from pydantic import BaseModel
from web_scraper import scraper_pipeline
from typing import List
from datetime import datetime
app = FastAPI()

def validate_root_url(url: str) -> str:
    """Normalize URL to ensure HTTPS scheme and proper formatting"""
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL cannot be empty"
        )

    parsed = urlsplit(url)

    # Add scheme if missing
    if not parsed.scheme:
        url = f"https://{url.lstrip('/')}"
        parsed = urlsplit(url)

    # Force HTTPS
    if parsed.scheme != 'https':
        url = parsed._replace(scheme='https').geturl()

    return url

@app.get("/check_root_url/{root_url}", response_model=Dict[str, bool])
def check_root_url(root_url: str):
    """
    Check if a root URL exists in the database
    Returns {'exists': true/false}
    """
    try:
        normalized_url = validate_root_url(root_url)
        with MongoDBManager() as db:
            exists = db.website_exists(normalized_url)
        return {"exists": exists}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/get_warning/{root_url}", response_model=Dict[str, str])
def get_warning(root_url: str):
    """
    Retrieve warning message for a root URL
    Returns {'message': 'warning text'} or 404 if not found
    """
    try:
        normalized_url = validate_root_url(root_url)
        with MongoDBManager() as db:
            website = db.get_website(normalized_url)

            if not website:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Website not found in database"
                )

            return {"message": website.get("message", "No message available")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )




# Request model for POST body
class WebsiteRequest(BaseModel):
    website: str

# Updated POST endpoint
@app.post("/add_website",
          status_code=status.HTTP_201_CREATED,
          response_model=Dict[str, Union[str, bool]])
def add_website(request: WebsiteRequest):
    """
    Add a new website using scraper pipeline
    Returns created entry with server-generated message
    """
    try:
        # Validate and normalize URL from request body
        normalized_url = validate_root_url(request.website)

        with MongoDBManager() as db:
            # Check for existing entry
            if db.website_exists(normalized_url):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Website already exists in database"
                )

            # Generate message through scraper pipeline
            try:
                message = scraper_pipeline(normalized_url)
                if not message:
                    raise ValueError("Scraper returned empty message")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Scraping failed: {str(e)}"
                )

            # Insert into database
            website_id = db.add_website(normalized_url, message)

            if not website_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create database entry"
                )

            return {
                "id": website_id,
                "url": normalized_url,
                "message": message,
                "success": True
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )




# Add response model for website data
class WebsiteResponse(BaseModel):
    id: str
    url: str
    message: str
    created_at: datetime

@app.get("/websites",
         response_model=List[WebsiteResponse],
         response_description="List of all monitored websites")
def get_all_websites():
    """
    Retrieve all websites from the database
    Returns complete list of monitored websites with their warnings
    """
    try:
        with MongoDBManager() as db:
            websites = db.get_all_websites()

            if not websites:
                return []

            # Convert to response model format
            return [
                {
                    "id": site["_id"],
                    "url": site["url"],
                    "message": site["message"],
                    "created_at": site["created_at"]
                } for site in websites
            ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve websites: {str(e)}"
        )
