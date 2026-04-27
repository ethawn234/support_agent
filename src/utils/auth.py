
import json
import os

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import build_gmail_service

load_dotenv()


_DECRYPTED_CREDS_FILE = os.path.join(os.path.dirname(__file__), "..", "src", "credentials.json")

def _authenticate_gmail_toolkit() -> GmailToolkit:
    with open(_DECRYPTED_CREDS_FILE) as f:
        all_creds = json.load(f)

    gmail_cred = next(c for c in all_creds if c.get("type") == "gmailOAuth2")
    oauth_data = gmail_cred["data"]
    token_data = oauth_data["oauthTokenData"]

    credentials = Credentials(
        token=None,
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=oauth_data["clientId"],
        client_secret=oauth_data["clientSecret"],
        scopes=["https://mail.google.com/"],
    )

    if not credentials.valid and credentials.refresh_token:
        credentials.refresh(Request())

    api_resource = build_gmail_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    return toolkit