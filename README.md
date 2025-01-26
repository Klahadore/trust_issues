# Trust Issues AI

## 📖 Overview
The **Trust Issues AI** is a project aimed at empowering users to make informed decisions about the platforms they use. By analyzing privacy policies, aggregating user reviews (via APIs like Trustpilot), and displaying insights in a responsive modal, this project highlights potential data and trust issues.

---

## 🚀 Features
1. **Privacy Warnings**: Fetches warnings and risks from an external API.
2. **Trustpilot Reviews Integration**: Gathers and analyzes user reviews for added insights.
3. **Interactive Modal**: Displays alerts and analysis in an easy-to-read modal on your browser.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
Start by cloning this repository to your local machine:
```bash
git clone https://github.com/yourusername/trust-issues-analyzer.git
cd trust-issues-analyzer
```

### 2. Install Requirements
Make sure you have Python installed. Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys
Create a .env file in the root directory of the project to store your API keys. Format the file like this:
```bash
FIRECRAWL_API_KEY = your key 
OPENAI_API_KEY = your key
MONGO_URI = your uri
```
### 4. Start the FastAPI Server
```bash
uvicorn main:app --reload 
or
fastapi run backend/server.py
```
### 5. Run the Localhost Website
```bash
run app.py
```



