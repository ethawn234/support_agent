import os

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import ChatOpenAI

load_dotenv()

portkey_api_key = os.getenv("PORTKEY_API_KEY")

if portkey_api_key is None:
    raise ValueError("PORTKEY_API_KEY environment variable is not set")

llm = ChatOpenAI(
    api_key=SecretStr(portkey_api_key),
    base_url=os.getenv("PORTKEY_URL", None),
    model="@azure-openai-eus2/gpt-5-mini",
    default_headers={
        "x-portkey-provider":"@azure-openai-eus2/gpt-5-mini"
    }
)