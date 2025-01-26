from typing import Dict, Union, Optional
from fastapi import FastAPI, HTTPException, status
from urllib.parse import urlsplit, urlparse
import asyncio
from starlette.responses import Content
from database import MongoDBManager
from pydantic import BaseModel
from web_scraper import scraper_pipeline, scrape_reviews_pipeline
from typing import List
from datetime import datetime

app = FastAPI()

class WebsiteRequest(BaseModel):
    website: str

class WebsiteMessageResponse(BaseModel):
    message: str
    extended_message: str
    reviews_message: Optional[str] = None
    reviews_extended_message: Optional[str] = None

class WebsiteResponse(WebsiteMessageResponse):
    id: str
    url: str
    created_at: datetime

def validate_root_url(url: str) -> str:
    """Normalize URL to ensure HTTPS scheme and proper formatting"""
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL cannot be empty"
        )

    parsed = urlsplit(url)

    if not parsed.scheme:
        url = f"https://{url.lstrip('/')}"
        parsed = urlsplit(url)

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
    Retrieve warnings - check DB first, then scrape live if missing
    """
    try:
        normalized_url = validate_root_url(root_url)
        with MongoDBManager() as db:
            website = db.get_website(normalized_url)

            if not website:
                message, extended_message = scraper_pipeline(normalized_url)
                return {
                    "message": message,
                    "extended_message": extended_message,
                    "reviews_message": None,
                    "reviews_extended_message": None
                }

            return {
                "message": website.get("message"),
                "extended_message": website.get("extended_message"),
                "reviews_message": website.get("reviews_message"),
                "reviews_extended_message": website.get("reviews_extended_message")
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving warning: {str(e)}"
        )

@app.post("/add_website",
          status_code=status.HTTP_201_CREATED,
          response_model=WebsiteResponse)
async def add_website(request: WebsiteRequest):
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
                # Robust domain extraction
                extract_domain = lambda url: urlparse(url.strip()).netloc or urlparse(f"https://{url.strip()}").netloc
                loop = asyncio.get_running_loop()

                scraper_future = loop.run_in_executor(
                    None,
                    lambda: scraper_pipeline(normalized_url)
                )

                reviews_future = loop.run_in_executor(
                    None,
                    lambda: scrape_reviews_pipeline(extract_domain(normalized_url))
                )

                (message, extended_message), (reviews_message, reviews_extended_message) = await asyncio.gather(
                    scraper_future,
                    reviews_future
                )

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Scraping failed: {str(e)}"
                )

            website_id = db.add_website(
                url=normalized_url,
                message=message,
                extended_message=extended_message,
                reviews_message=reviews_message,
                reviews_extended_message=reviews_extended_message
            )

            return {
                "id": website_id,
                "url": normalized_url,
                "message": message,
                "extended_message": extended_message,
                "reviews_message": reviews_message,
                "reviews_extended_message": reviews_extended_message,
                "created_at": datetime.utcnow()
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@app.get("/get_websites",
         response_model=List[WebsiteResponse],
         response_description="List of all monitored websites")
def get_all_websites():
    """
    Retrieve all websites from the database
    """
    try:
        with MongoDBManager() as db:
            websites = db.get_all_websites()

            return [
                {
                    "id": site["_id"],
                    "url": site["url"],
                    "message": site["message"],
                    "extended_message": site["extended_message"],
                    "reviews_message": site["reviews_message"],
                    "reviews_extended_message": site["reviews_extended_message"],
                    "created_at": site["created_at"]
                } for site in websites
            ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve websites: {str(e)}"
        )

class AnalyzeReviewsModel(BaseModel):
    reviews_message: Optional[str] = None
    reviews_extended_message: Optional[str] = None

@app.get("/analyze-reviews/{website}", response_model=AnalyzeReviewsModel)
def analyze_reviews(website: str):
    try:
        domain = urlparse(website.strip()).netloc or urlparse(f"https://{website.strip()}").netloc
        reviews_message, reviews_extended_message = scrape_reviews_pipeline(domain)

        return {
            "reviews_message": reviews_message,
            "reviews_extended_message": reviews_extended_message
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Review analysis failed: {str(e)}"
        )
