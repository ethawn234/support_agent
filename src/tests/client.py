import os
from dotenv import load_dotenv
from portkey_ai import Portkey
from anthropic import Anthropic

load_dotenv()

portkey_api_key = os.getenv("PORTKEY_API_KEY", "")
if portkey_api_key is None:
    raise ValueError("PORTKEY_API_KEY environment variable is not set")


def create_client():
    client = Anthropic(
        base_url="https://portkeygateway.perficient.com",
        api_key=portkey_api_key,
        default_headers={"x-portkey-api-key": portkey_api_key, "x-portkey-provider": "@aws-bedrock-use2/us.anthropic.claude-3-haiku-20240307-v1:0"}
    )

    return client
