import json
from typing import Literal, Type

from langgraph.types import Command, interrupt
from langgraph.graph import END
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_community.gmail.create_draft import GmailCreateDraft
from langchain_google_community.gmail.send_message import GmailSendMessage


from agent.state import AgentState, EmailClassification
from agent.llm import llm

# entry
def read_email(state: AgentState):
    """Pre-processor for emails related to IT support. Basic validation (eg PII, Prompt Injection, IT support relevance (how to determine?)) can be added here as well."""
    print(f"\n\nIn read_email()...")

    try:
        if state.raw_email is not None:
            request = state.raw_email[0]

            if "support" in request['subject'] or "Support" in request['subject']:
                print(f"\n\nEmail is a valid IT Support request: {request}")

        return state
    except Exception as e:
        print(f"Error in read_email: {e}")
        return _handle_error(state, content=state.raw_email, error_msg=e, goto="send_slack_notification")

def classification(state: AgentState) -> Command[Literal["send_slack_notification", "request_email_clarification", "create_ticket"]]:
    """Classify incoming email and determine nature of the request, urgency, and category. This will help determine the appropriate next steps for resolution, such as whether human approval is needed, whether clarification is needed from the user, or whether a ticket can be automatically created and relevant teams notified.

    1. If classified:
        a. if low-priority, goto create_ticket
        b. if high-priority (or risky -> impact), goto human_review
    2. If more info required:
        - goto request_email_clarification
    """
    print("\n\nIn classification()") 
    try:
        prompt = SystemMessage(f"""Classify the following support request into one of the following categories: 1) password_issue, 2) hardware_issue, 3) software_issue 4) general_inquiry. 
        
        Request: {state.email_content}
        
        Analyze this IT request and provide the classification, including intent, priority, category, and summary.

        Example output:
        ```json
        [
            {{
                "intent": "The intent of the email (e.g., password reset, software issue, hardware issue)",
                "urgency": "The extent to which resolution of an incident can bear delay (decreasing urgency 1 to 3)",
                "category": "Category of the issue: ["network", "software", "hardware", "password_reset", "inquiry", "database"]",
                "analysis": "Agent's analysis and recommendation",
                "priority": "Severity of request (decreasing priority 1 - 5)",
                "impact": "The effect of an issue on the business (decreasing impact from 1 - 3)",
                "needs_info": "Boolean indicating if more information is required from the requestor"
            }}
        ]
        ```
        """)
        
        # if high-priority, goto = human_review
        
        # if low-priority, goto = create_ticket
        response = llm.with_structured_output(EmailClassification).invoke(prompt.content)
        impact = response["impact"]
        needs_info = response["needs_info"]

        goto: Literal["send_slack_notification", "request_email_clarification", "create_ticket"]
        if needs_info:
            goto = "request_email_clarification"
        else:
            goto = "create_ticket"

        return Command(
            update={ "classification": response },
            goto=goto
        )
    
    except Exception as e:
        # handle 429
        print(f"Error in classification: {e}")
        return _handle_error(state, content=response, error_msg=e, goto="send_slack_notification")


# should be a tool, not a node maybe. Depends if agent should call or we want max deterministic flow
def request_email_clarification(state) -> Command:
    """Request clarification from user if email content is insufficient for classification or issue resolution."""
    try:
        # gmail_draft_service = GmailCreateDraft(api_resource=state.toolkit.api_resource)
        gmail_send_service = GmailSendMessage(api_resource=state.toolkit.api_resource)

        # body requesting user provide more info
        to = [state['raw_email'].sender]
        subject = "More information is needed to process your support request"
        message = f"""
        Hi {to},

        IT Support has received your request. To further process your request, more information is required.

        Please provide the following information:
        {state['classification'].needs_info}
    """
        # create draft
        # body = gmail_draft_service.run({
        #     "message": message,
        #     "to": to,
        #     "subject": subject
        # })
        # print(f"Additional info email drafted: {body}")
        # draft_response = body['message'].raw

        # send email
        send_email = gmail_send_service.run({
            "message": message,
            "to": to,
            "subject": subject
        })

        print(f"Additional info email sent to user: {send_email}")
        
        return Command(
            update={state['messages']: AIMessage(content=f"{send_email}")},
            goto=END
        )

    except Exception as e:
        print(f"Error in request_email_clarification: {e}")
        return _handle_error(state, content=send_email, error_msg=e, goto="send_slack_notification")

def create_ticket(state) -> Command:
    """Create a ServiceNow incident ticket based on the classification."""
    try:
        print(f"\nIn create_ticket...\n")
        return Command(
            update=state,
            goto=""
        )
    except Exception as e:
        print(f"Error in create_ticket: {e}")
        return _handle_error(state, content="draft_ticket", error_msg=e, goto="send_slack_notification")

def _handle_error(state, content, error_msg, goto) -> Command[Literal["send_slack_notification", "request_email_clarification", "create_ticket"]]:
    return Command(
        update=state['messages'].append(SystemMessage(content=f"There was an error.\nContent={content}\nError: {error_msg}")),
        goto=goto
    )

def search_kb(state):
    """Search IT support knowledge base for relevant articles based on email content and classification. TBD: Probably do a similarity search based on email embedding and kb article embeddings?"""


def send_slack_notification(state):
    """Send a notification to the IT support team in Slack with details of the new incident."""

def human_review(state):
    """Human review for issues creating ticket, classification, and any other failures"""


# def handle_breaker(state):
#     """Each risky operation (llm call, tool use) gets a separate CB state. Handle all transitions based on operation outcome.
    
#     TODO: Need to look into the Fault Tolerance features in langgraph to see if this can be handled more elegantly with built in CB states or middlewares. Otherwise, may need to create custom CB states and handle transitions manually in this node.
#     """

# def send_logs(state):
#     """Send logs and traces of infrastructure and LLM.
    
#     TODO: This node may not be needed. Look into middlewares (possibly custom) or Fault Tolerance features in langgraph. Log/Traces seem to be handled by tacking on some setting or middleware to the nodes.
#     """


# def validate_issue(state: AgentState):
#     """Analyze the issue in the email and determine appropriate next steps for resolution.
    
#     TODO: validate_issue() part may also be better handled with middleware or something else. Why? LangGraph provides built in support for guardrails and validation, so it may be possible to use those features instead of manually validating the LLM output in a node. TBD after further investigation into LangGraph features. Just for example, see with_structured_output().

#     """
#     pprint('\n\nAnalyzing LLM output...')

#     try:        
#         if state.classification is not None:
#             if EmailClassification.model_validate_json(json.dumps(state.classification.__dict__)):
#                 print('\n\nLLM output validated against classification schema...continuing.')
#                 return state
#     except Exception as e:
#         print(f'\n\nInterrupting as LLM response JSON could not be validated: {e}')
#         interrupt(f"\n\nLLM response could not be validated: {json.dumps(state)}")
#         # TODO: rerun prompt through LLM if output does not follow EmailClassification schema
