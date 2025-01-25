from typing import Dict, Union
from fastapi import FastAPI, HTTPException, status
from urllib.parse import urlsplit
from database import MongoDBManager
from pydantic import BaseModel
from web_scraper import scraper_pipeline
from typing import List
from datetime import datetime
app = FastAPI()

class WebsiteRequest(BaseModel):
    website: str

class WebsiteMessageResponse(BaseModel):
    message: str
    extended_message: str

class WebsiteResponse(WebsiteMessageResponse):
    id: str
    url: str
    created_at: datetime
# Updated POST endpoint

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

@app.get("/get_warning/{root_url}", response_model=WebsiteMessageResponse)
def get_warning(root_url: str):
    """
    Retrieve both message versions for a root URL
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

            return {
                "message": website.get("message"),
                "extended_message": website.get("extended_message")
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )




# Request model for POST body

@app.post("/add_website",
          status_code=status.HTTP_201_CREATED,
          response_model=WebsiteResponse)
def add_website(request: WebsiteRequest):
    """
    Add website with auto-generated messages
    """
    try:
        normalized_url = validate_root_url(request.website)

        with MongoDBManager() as db:
            if db.website_exists(normalized_url):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Website already exists in database"
                )

            try:
                # Assume scraper returns tuple/dict with both messages
                message, extended_message = scraper_pipeline(normalized_url)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Scraping failed: {str(e)}"
                )

            website_id = db.add_website(
                url=normalized_url,
                message=message,
                extended_message=extended_message
            )

            return {
                "id": website_id,
                "url": normalized_url,
                "message": message,
                "extended_message": extended_message,
                "created_at": datetime.utcnow()
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )



# Add response model for website data

@app.get("/get_websites",
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
                    "extended_message": site["extended_message"],
                    "created_at": site["created_at"]
                } for site in websites
            ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve websites: {str(e)}"
        )
