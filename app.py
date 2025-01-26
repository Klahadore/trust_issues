import streamlit as st
from urllib.parse import urlparse
from backend.web_scraper import scraper_pipeline, scrape_reviews_pipeline
from openai import OpenAI
import os
import asyncio

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize DeepSeek client
client = OpenAI(
    base_url="https://api.deepseek.com/",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Configure Streamlit app
st.set_page_config(page_title="Policy Analyzer", page_icon="⚖️")
st.title("Website Policy Analyzer")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "policies" not in st.session_state:
    st.session_state.policies = None
if "reviews" not in st.session_state:
    st.session_state.reviews = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

async def run_analysis(website_url):
    """Async wrapper for scraping operations"""
    parsed_url = urlparse(website_url)
    loop = asyncio.get_event_loop()

    try:
        # Run both scrapers concurrently
        policies, reviews = await asyncio.gather(
            loop.run_in_executor(None, scraper_pipeline, parsed_url.netloc),
            loop.run_in_executor(None, scrape_reviews_pipeline, parsed_url.netloc)
        )

        st.session_state.policies = policies
        st.session_state.reviews = reviews
        st.session_state.analysis_done = True

    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        st.session_state.analysis_done = False
    finally:
        st.session_state.running = False

# Website input and scraping
with st.sidebar:
    st.header("Configure Analysis")
    website_url = st.text_input(
        "Enter website URL (e.g., ebay.com):",
        placeholder="example.com",
        key="website_input"
    )

    if st.button("Analyze Website") and website_url:
        if not website_url.startswith(('http://', 'https://')):
            website_url = f'https://{website_url}'

        parsed_url = urlparse(website_url)
        if not parsed_url.netloc:
            st.error("Invalid URL format")
        else:
            st.session_state.running = True
            asyncio.run(run_analysis(website_url))

if st.session_state.get('running'):
    with st.sidebar:
        st.spinner("Analyzing website content...")

# Main chat interface
if st.session_state.analysis_done:
    # Create system prompt with policies
    system_prompt = "You are a legal expert analyzing website policies and consumer reviews. "

    if st.session_state.policies:
        system_prompt += f"""
        POLICIES ANALYSIS:
        {st.session_state.policies[0]}
        {st.session_state.policies[1]}
        """

    if st.session_state.reviews:
        system_prompt += f"""
        CONSUMER REVIEWS ANALYSIS:
        {st.session_state.reviews[0]}
        {st.session_state.reviews[1]}
        """

    system_prompt += "\nProvide concise, accurate answers about potential risks and policy details."

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about the website's policies or reviews..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            full_messages = [
                {"role": "system", "content": system_prompt},
                *[{"role": m["role"], "content": m["content"]}
                  for m in st.session_state.messages]
            ]

            try:
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=full_messages,
                    stream=True,
                    timeout=30  # Add timeout
                )

                response = st.write_stream(stream)

            except Exception as e:
                response = f"Error generating response: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": response})

elif not st.session_state.analysis_done and not st.session_state.get('running'):
    st.info("Enter a website URL and click 'Analyze Website' to begin")
