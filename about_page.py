import streamlit as st

# st.set_page_config(page_title="About Trust Issues", page_icon="🔍")

def about_page():
    # Configure Streamlit app
    st.title("About Trust Issues")

    # Project Description
    st.markdown("""
    ## 🔍 What is Trust Issues?

    **Trust Issues** is a browser extension and web tool designed to help users make informed decisions before signing up for new websites.
    It analyzes the fine print in privacy policies and terms and conditions, warning you about any untrustworthy or risky clauses hidden in the text.

    ### 🛡️ Why Trust Issues?
    When you sign up for a new website, you're often required to agree to lengthy and complex legal documents.
    These documents can contain clauses that:
    - Compromise your privacy
    - Expose you to unnecessary risks
    - Allow the website to misuse your data

    Trust Issues reads these documents for you and highlights potential red flags, so you can make an informed decision before proceeding.

    ### 🚀 How It Works
    1. **Automatic Detection**: When you visit a website, Trust Issues automatically detects sign-up forms and buttons.
    2. **Policy Analysis**: It scrapes and analyzes the website's privacy policy and terms of service.
    3. **Review Analysis**: It also analyzes user reviews to provide additional context about the website's trustworthiness.
    4. **Warning System**: If any red flags are found, Trust Issues displays a warning with detailed explanations.
    5. **User-Friendly Interface**: All information is presented in an easy-to-understand format with expandable sections for more details.

    ### 💡 Key Features
    - **Fine Print Analysis**: Automatically scans and analyzes legal documents.
    - **Review Insights**: Aggregates and analyzes user reviews for additional context.
    - **Real-Time Warnings**: Provides instant warnings when risky clauses are detected.
    - **User-Friendly Interface**: Presents complex legal information in a simple, understandable way.
    - **Customizable Settings**: Allows users to configure what types of warnings they want to see.

    ### 🛠️ Technologies Used
    - **Natural Language Processing (NLP)**: To analyze and summarize legal documents.
    - **Web Scraping**: To extract privacy policies, terms of service, and user reviews.
    - **Streamlit**: For the web-based analysis tool.
    - **Browser Extension**: For real-time warnings while browsing.

    ### 🙌 Who Is It For?
    Trust Issues is for anyone who:
    - Values their privacy and security online
    - Wants to avoid hidden risks in legal documents
    - Prefers to make informed decisions before signing up for new services
    - Finds legal documents too complex or time-consuming to read

    ### 📜 Example Use Cases
    - **Signing Up for a New Service**: Before creating an account, Trust Issues warns you about any problematic clauses in the terms of service.
    - **Online Shopping**: It analyzes the privacy policy of an e-commerce site to ensure your data won't be misused.
    - **Social Media Platforms**: It highlights any concerning clauses in the terms of service before you agree to them.

    ### 🌐 Get Started
    To start using Trust Issues:
    1. Install the browser extension.
    2. Visit any website with a sign-up form.
    3. Let Trust Issues analyze the fine print for you.
    4. Make informed decisions based on the warnings and insights provided.

    ### 📧 Contact Us
    Have questions or feedback? Reach out to us at [support@trustissues.com](mailto:support@trustissues.com).

    ### 🔗 GitHub Repository
    Check out the project on GitHub: [Trust Issues GitHub Repo](https://github.com/trust-issues)
    """)

    # Add a divider for visual separation
    st.divider()

    # Footer
    st.markdown("""
    ---
    **Trust Issues** is an open-source project developed to promote transparency and trust online.
    We believe everyone deserves to know what they're agreeing to when using online services.
    """)
