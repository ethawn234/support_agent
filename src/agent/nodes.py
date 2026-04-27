import os
import json
from sys import exception

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
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
    base_url=os.getenv("PORTKEY_API_URL", None),
)

def input_guardrail(state):
    """Guardrail to ensure agent only processes emails related to IT support."""
    request = state.messages[-1].content.lower()
    if "support" in request:
        return "proceed"
    else:
        interrupt("Email does not appear to be related to IT support. Ignoring.")

def classification(state):
    """Classify incoming email and determine next step in workflow."""
    structured_llm = llm.with_structured_output(EmailClassification)

    request = state.messages[-1].content.lower()
    if "password" in request or "reset" in request:
        return "password_issue"
    
    """Use LLM to classify request"""
    prompt = f"""Classify the following support request into one of the following categories: 
    1) password_issue, 2) hardware_issue, 3) software_issue 4) general_inquiry. 
    Request: {request}

    Analyze this IT request and provide the classification, including intent, urgency, category, and summary.
    """

    response = llm.invoke(prompt)
    classification = response.content[0]
    state.comment_history.append(response)
    
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
