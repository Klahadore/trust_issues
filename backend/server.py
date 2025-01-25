from typing import Dict, Union
from fastapi import FastAPI, HTTPException, status
from urllib.parse import urlsplit
from database import MongoDBManager
from pydantic import BaseModel
from web_scraper import scraper_pipeline

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

class WebsiteCreateRequest(BaseModel):
    message: str

# Update the POST endpoint
@app.post("/add_website/{root_url}",
          status_code=status.HTTP_201_CREATED,
          response_model=Dict[str, Union[str, bool]])
def add_website(root_url: str, data: WebsiteCreateRequest):
    """
    Add a new website to the database
    Returns created website ID and URL
    """
    try:
        normalized_url = validate_root_url(root_url)

        with MongoDBManager() as db:
            # Check for existing website first
            if db.website_exists(normalized_url):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Website already exists in database"
                )

            # Insert new website
            website_id = db.add_website(normalized_url, data.message)

            if not website_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create website entry"
                )

            return {
                "id": website_id,
                "url": normalized_url,
                "success": True
            }

    except HTTPException as he:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )
# Update MongoDBManager to support context manager
