import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.environ.get("AI_API_KEY"),
    temperature=0.7,
)