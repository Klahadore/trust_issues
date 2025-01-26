import streamlit as st
from urllib.parse import urlparse
from backend.web_scraper import scraper_pipeline, scrape_reviews_pipeline
from openai import OpenAI
import os

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

# Website input and scraping
with st.sidebar:
    st.header("Configure Analysis")
    website_url = st.text_input(
        "Enter website URL (e.g., ebay.com):",
        placeholder="example.com",
        key="website_input"
    )

    if st.button("Analyze Website"):
        if website_url:
            try:
                # Validate URL
                if not website_url.startswith(('http://', 'https://')):
                    website_url = f'https://{website_url}'

                parsed_url = urlparse(website_url)
                if not parsed_url.netloc:
                    raise ValueError("Invalid URL format")

                # Scrape policies
                with st.spinner("Analyzing website policies..."):
                    st.session_state.policies = scraper_pipeline(parsed_url.netloc)

                # Scrape reviews
                with st.spinner("Checking consumer reviews..."):
                    st.session_state.reviews = scrape_reviews_pipeline(parsed_url.netloc)

                st.success("Analysis complete!")

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
        else:
            st.warning("Please enter a website URL")

# Main chat interface
if st.session_state.policies or st.session_state.reviews:
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

            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=full_messages,
                stream=True,
            )

            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("Enter a website URL and click 'Analyze Website' to begin")
