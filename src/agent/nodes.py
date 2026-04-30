import os
import json
from sys import exception
from pprint import pprint

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field, SecretStr
from typing import List, Optional, Literal
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from langchain_openai import ChatOpenAI
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.search import GmailSearch
from langchain_google_community.gmail.utils import build_gmail_service
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, END, START

from agent.state import AgentState, EmailState, EmailClassification

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

def input_guardrail(state):
    """Guardrail to ensure agent only processes emails related to IT support."""
    request = state.messages[-1].lower()
    print(f"request returned: {request}")
    if "support" in request:
        return state
    else:
        interrupt("Email does not appear to be related to IT support. Ignoring.")

# def parse_email(state: SupportState) -> SupportState:
#     """Extract structured information from customer email."""
#     try:
#         print("Inside Node: parse_email")
#         prompt = PARSE_EMAIL_PROMPT.format(
#             subject=state["subject"], email_body=state["email_body"]
#         )
#         response = llm.with_structured_output(EmailParseOutput).invoke(prompt)

#         return {
#             **state,
#             "problem": response.problem,
#             "sentiment": response.sentiment,
#             "tracking_number": response.tracking_number,
#             "order_id": response.order_id,
#         }
#     except Exception as e:
#         print(f"parse_email error: {e}")
#         return state


def classification(state):
    """Classify incoming email and determine next step in workflow."""
    
    prompt = f"""Classify the following support request into one of the following categories: 
    1) password_issue, 2) hardware_issue, 3) software_issue 4) general_inquiry. 
    
    Request: {state.messages[-1]}

    Analyze this IT request and provide the classification, including intent, urgency, category, and summary.
    """
    try:
        response = llm.with_structured_output(EmailClassification).invoke(prompt)
        pprint(f'Checking response body structure: {response}')
        if response:
            state.messages.append(response)
    except Exception as e:
        # handle 429
        print(f'Could not get LLM classifiction: {e}')
        # handle 500s

        # update cb state
    pprint(f'works up to in classification(), state: {state}')
    return state

def analyze_issue(state):
    """Analyze the issue in the email and determine appropriate next steps for resolution."""

def output_guardrail(state):
    """Guardrail to ensure agent only takes actions that are supported by the tools available."""

def approval(state):
    """human approval for non low priority tickets."""

def create_ticket(state):
    """Create a ServiceNow incident ticket based on the email content and classification."""

def send_slack_notification(state):
    """Send a notification to the IT support team in Slack with details of the new incident."""

def handle_breaker(state):
    """Each risky operation (llm call, tool use) gets a separate CB state. Handle all transitions based on operation outcome."""