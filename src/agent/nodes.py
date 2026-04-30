import os
from pprint import pprint
import json

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langgraph.types import Command, interrupt
from langchain.messages import SystemMessage, HumanMessage

from agent.state import AgentState, EmailClassification

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

def input_guardrail(state: AgentState):
    """Guardrail to ensure agent only processes emails related to IT support."""
    print(f"\n\nIn input_guardrail()...")
    if state.raw_email is not None:
        request = state.raw_email[0]
        
    if "support" in request['subject'] or "Support" in request['subject']:
        print("\n\nEmail is a valid IT Support request. Continuing...")
        return {"is_valid_req": True}
    else:
        print("\n\nInvalid email type. 'Support' not found in subject. Interrupting...")
        interrupt("Email does not appear to be related to IT support. Ignoring.")


def classification(state: AgentState):
    """Classify incoming email and determine next step in workflow."""
    print("\n\nIn classification()")
    
    try:
        prompt = SystemMessage(f"""Classify the following support request into one of the following categories: 1) password_issue, 2) hardware_issue, 3) software_issue 4) general_inquiry. 
        
        Request: {state.email_content}

        Analyze this IT request and provide the classification, including intent, urgency, category, and summary.
        """)
        state.messages = [prompt]
        response = llm.with_structured_output(EmailClassification).invoke(prompt.content)
        if response:
            pprint(f'\n\nLLM Classification response: {response}')
            print('\n\nUser issue classified by LLM. Continuing...')
            return {"classification": response}
        else:
            return {"classification": None}
    except Exception as e:
        # handle 429
        print(f'Could not get LLM classifiction: {e}')
        # handle 500s

        # update cb state

def validate_issue(state: AgentState):
    """Analyze the issue in the email and determine appropriate next steps for resolution."""
    pprint('\n\nAnalyzing LLM output...')

    try:        
        if state.classification is not None:
            if EmailClassification.model_validate_json(json.dumps(state.classification.__dict__)):
                print('\n\nLLM output validated against classification schema...continuing.')
                return state
    except Exception as e:
        print(f'\n\nInterrupting as LLM response JSON could not be validated: {e}')
        interrupt(f"\n\nLLM response could not be validated: {json.dumps(state)}")
        # TODO: rerun prompt through LLM if output does not follow EmailClassification schema


def output_guardrail(state):
    """Guardrail to ensure agent only takes actions that are supported by the tools available."""
    print(f"In output_guardrail checking state: {state}")

def approval(state):
    """human approval for non low priority tickets."""

def create_ticket(state):
    """Create a ServiceNow incident ticket based on the email content and classification."""

def send_slack_notification(state):
    """Send a notification to the IT support team in Slack with details of the new incident."""

def handle_breaker(state):
    """Each risky operation (llm call, tool use) gets a separate CB state. Handle all transitions based on operation outcome."""

def send_logs(state):
    """Send logs and traces of infrastructure and LLM"""