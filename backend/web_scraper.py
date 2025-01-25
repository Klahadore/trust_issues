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
    max_tokens=8000
)


app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

class DefaultSchema(BaseModel):
    privacy_policy: str
    terms_and_conditions: str

class Default_Return_Schema(BaseModel):
    message: str
    extended_message: str

class Check_URL_Schema(BaseModel):
    valid: bool

def scrape_root_url(url: str, schema):
    data = app.extract([url], {'prompt': 'Look in the footer of the website. Ignore links that are not of the same root domain as the site. Return "null" if you can\'t find one of the links. There is no shame in not finding one of the links.links that are just privacy, privacy policy, are the same. terms of use, terms and conditions, are the same', 'schema': schema.model_json_schema()})
    print(data)
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


import re
from fuzzywuzzy import fuzz
from urllib.parse import urlparse

def find_policy_urls(urls):
    """
    Find URLs that are likely to be privacy policies or terms and conditions
    using fuzzy string matching.

    Args:
        urls (list): List of URLs to search

    Returns:
        list: Filtered list of URLs likely to be policy documents
    """
    # List of potential keywords for privacy policies and terms
    policy_keywords = [
        # Privacy Policy variations
        'privacy', 'privacy-policy', 'privacy_policy', 'privacypolicy',
        'data-protection', 'data_protection', 'dataprotection',
        'privacy-notice', 'privacy_notice', 'privacynotice',

        # Terms and Conditions variations
        'terms', 'terms-of-service', 'terms_of_service', 'termsofservice',
        'terms-and-conditions', 'terms_and_conditions', 'termsandconditions',
        'user-agreement', 'user_agreement', 'useragreement',
        'legal', 'tos', 'conditions', 'agreement'
    ]

    # Function to check if a URL is likely a policy document
    def is_policy_url(url):
        # Parse the URL to extract its path
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        # Remove leading/trailing slashes and split path
        path_parts = path.strip('/').split('/')

        # Check each part of the path against keywords
        for part in path_parts:
            # Try exact and partial matches
            for keyword in policy_keywords:
                # Exact match
                if part == keyword:
                    return True

                # Fuzzy match with high threshold
                if fuzz.ratio(part, keyword) > 80:
                    return True

        return False

    # Filter URLs using the is_policy_url function
    policy_urls = [url for url in urls if is_policy_url(url)]

    return policy_urls



def try_getting_other_urls(base_url: str):
    map_result = app.map_url(base_url, params={
        'includeSubdomains': True,
	'sitemapOnly': True,
	'search': "privacy policy and terms"
    })
    return map_result['links']

class Classify_URLS_schema(BaseModel):
    privacy_policy_url: str
    terms_url: str

def get_URLS(urls: list[str]) -> tuple[str,str]:
    classify_urls_template = ChatPromptTemplate([
       ('system', 'You are given a list of urls, return the best match url for privacy policy, and the best match url for the terms and conditions. Keep in mind sometimes the URLs won\'t exactly match, so just try your best'),
       ('human', 'Here are the URLs:{urls}')
    ])
    prompt = classify_urls_template.invoke({'urls': ', '.join(urls)})
    structured_llm = llm.with_structured_output(Classify_URLS_schema)
    response = structured_llm.invoke(prompt)
    return (response.privacy_policy_url, response.terms_url)

def scraper_pipeline(root_url: str):
    root_url = validate_url(None, root_url)

    structured_llm = llm.with_structured_output(Default_Return_Schema)

    try:
        raw_urls = try_getting_other_urls(root_url)
        privacy_policy_url, terms_url = get_URLS(raw_urls)
    except:
        print(f"couldn't scrape root url {root_url}, return AI generated message")
        simple_template = ChatPromptTemplate([
            ('system', "You are a helpful lawyer who is reviewing these terms and conditions, and privacy policies for potential data and trust misues that is not clear to the user, warn the client of the top three things you see for the given website. With a slight bias for negativity. Expose the websites. Be concise. "),
            ('human', "For the website {root_url}, please give me a short message being as concise, and as sharp as possible, and an extended message with more nuance, explaining what is going on. ")
        ])

        prompt = simple_template.invoke({'root_url': root_url})
        response = structured_llm.invoke(prompt)
        return (response.message, response.extended_message)



    terms_and_conditions_text = scrape_for_markdown(terms_url)['markdown']
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

    response = structured_llm.invoke(prompt)

    # Check if response failed


    return (response.message, response.extended_message)



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
   # print(scraper_pipeline("imgacademy.com"))
    # urls = try_getting_other_urls("imgacademy.com")
    # print(validate_url("/terms", "google.com"))


    # # Find policy URLs
    # found_policy_urls = find_policy_urls(urls)
    # print("Policy URLs found:")
    # for url in found_policy_urls:
    #     print(url)

    # print(get_terms_URLS(found_policy_urls))
    print(scraper_pipeline("linkedin.com"))
