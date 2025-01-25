from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from urllib.parse import urlsplit, urlunsplit, urljoin
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv

load_dotenv()

deepseek_api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {bool(deepseek_api_key)}")  # Should show True

# Initialize LLM with proper configuration
llm = BaseChatOpenAI(
    model='deepseek-chat',
    api_key=deepseek_api_key,  # Now properly set
    base_url='https://api.deepseek.com/',  # Added /v1 to endpoint
    max_tokens=1024
)


app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

class DefaultSchema(BaseModel):
    privacy_policy: str
    terms_and_conditions: str

def scrape_root_url(url: str, schema):
    data = app.extract([url], {'prompt': '', 'schema': schema.model_json_schema()})

    return data

def scrape_for_markdown(url: str):
    response = app.scrape_url(url=url, params={
	'formats': [ 'markdown' ],
    })
    return response


def validate_url(input_url: Optional[str], root_url: str) -> str:
    """
    Validates and constructs a full HTTPS URL.

    1. If input_url starts with https://, returns it directly
    2. If input_url is a partial URL (e.g., "/path"):
       - Combines it with the provided root_url
       - Ensures the final URL uses HTTPS
    3. If input_url uses other schemes (http://, ftp://), converts to HTTPS

    Args:
        input_url: URL to validate
        root_url: Base URL to use for partial paths

    Returns:
        Full HTTPS URL
    """
    parsed_input = urlsplit(input_url)

    # Handle full URLs
    if parsed_input.scheme:
        if parsed_input.scheme != 'https':
            return urlunsplit(parsed_input._replace(scheme='https'))
        return input_url

    # Handle partial URLs
    # Ensure root URL has a scheme
    parsed_root = urlsplit(root_url)
    if not parsed_root.scheme:
        root_url = f'https://{root_url.lstrip("/")}'

    # Combine URLs and force HTTPS
    combined = urljoin(root_url, input_url)
    parsed_combined = urlsplit(combined)

    if parsed_combined.scheme != 'https':
        return urlunsplit(parsed_combined._replace(scheme='https'))

    return combined

class return_schema(BaseModel):
    pass

def scraper_pipeline(root_url: str):
    root_url = validate_url(None, root_url)
    scrape_root = scrape_root_url(root_url, DefaultSchema)

    privacy_policy_url = validate_url(scrape_root['data']['privacy_policy'], root_url)
    terms_and_conditions_url = validate_url(scrape_root['data']['terms_and_conditions'], root_url)

    terms_and_conditions_text = scrape_for_markdown(terms_and_conditions_url)['markdown']
    privacy_policy_text = scrape_for_markdown(privacy_policy_url)['markdown']

    flagging_template = ChatPromptTemplate([
        (
            'system',
            'You are a helpful lawyer who is reviewing these terms and conditions, and privacy policies for '
            'potential data misuse that is not clear to the user. Warn your client of the top three things you see '
            'in a simple and concise sentence.'
        ),
        (
            'human',
            'Here are the terms and conditions: {terms_and_conditions}, and here is the privacy policy: {privacy_policy}.'
        )
    ])

    prompt = flagging_template.invoke({'terms_and_conditions': terms_and_conditions_text, 'privacy_policy': privacy_policy_text})
    response = llm.invoke(prompt)

    return response.content

if __name__ == "__main__":
    # root_url = "https://google.com"
    # scrape_root = scrape_root_url(root_url, DefaultSchema)
    # privacy_policy_url = scrape_root['data']['privacy_policy']
    # terms_and_conditions_url = scrape_root['data']['terms_and_conditions']
    # print(privacy_policy_url, terms_and_conditions_url)
    # scrape_terms = scrape_for_markdown(terms_and_conditions_url)
    # scrape_policy = scrape_for_markdown(privacy_policy_url)
    # print(scrape_terms['markdown'])
    #
    print(scraper_pipeline("ebay.com"))

    # print(validate_url("/terms", "google.com"))
