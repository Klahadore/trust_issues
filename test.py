import os
from dotenv import load_dotenv
from langchain_openai.chat_models.base import BaseChatOpenAI
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
deepseek_api_key = os.getenv("OPENAI_API_KEY")

llm = BaseChatOpenAI(
    model='deepseek-chat', 
    openai_api_key= deepseek_api_key, 
    openai_api_base='https://api.deepseek.com',
    max_tokens=1024
)


response = llm.invoke("Hi!")
print(response.content)

# flagging_template = PromptTemplate(
#     input_variables=["text"],
#     template=(
#         "You are a lawyer. Analyze the following terms and conditions and determine if it contains "
#         "misleading information. If so, flag it and provide a brief explanation "
#         "of why it is flagged. Respond with either:\n"
#         "- 'Safe: [Reason why the content is safe]'\n"
#         "- 'Flagged: [Reason why the content is harmful or misleading]'\n\n"
#         "Text:\n{text}"
#     )
# )

# flagging_chain = LLMChain(
#     llm=llm,
#     prompt=flagging_template
# )

# sample_text = "This product guarantees 100% cancer cure instantly. No scientific evidence required!"

# response = flagging_chain.run({"text": sample_text})
# print(response)