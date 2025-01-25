import os
from dotenv import load_dotenv
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables FIRST
load_dotenv()  # Make sure this is called before accessing os.getenv()

# Verify keys are loading correctly
deepseek_api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {bool(deepseek_api_key)}")  # Should show True

# Initialize LLM with proper configuration
llm = BaseChatOpenAI(
    model='deepseek-chat',
    api_key=deepseek_api_key,  # Now properly set
    base_url='https://api.deepseek.com/',  # Added /v1 to endpoint
    max_tokens=1024
)

# Test call
# try:
#     response = llm.invoke("Hi!")
#     print(response.content)
# except Exception as e:
#     print(f"Error: {e}")

flagging_template = PromptTemplate(
    input_variables=["text"],
    template=(
        "You are a lawyer. Analyze the following terms and conditions and determine if it contains "
        "misleading information. If so, flag it and provide a brief explanation "
        "of why it is flagged. Respond with either:\n"
        "- 'Safe: [Reason why the content is safe]'\n"
        "- 'Flagged: [Reason why the content is harmful or misleading]'\n\n"
        "Text:\n{text}"
    )
)
flagging_template = PromptTemplate(
    input_variables=["text"],
    template=(
        "You are a lawyer. Analyze the following terms and conditions and determine if it contains "
        "misleading information. If so, flag it and provide a brief explanation "
        "of why it is flagged. Respond with either:\n"
        "- 'Safe: [Reason why the content is safe]'\n"
        "- 'Flagged: [Reason why the content is harmful or misleading]'\n\n"
        "Text:\n{text}"
    )
)

flagging_chain = LLMChain(
    llm=llm,
    prompt=flagging_template
)
flagging_chain = LLMChain(
    llm=llm,
    prompt=flagging_template
)

sample_text = "This product guarantees 100% cancer cure instantly. No scientific evidence required!"
sample_text = "This product guarantees 100% cancer cure instantly. No scientific evidence required!"

response = flagging_chain.invoke({"text": sample_text})
print(response)
