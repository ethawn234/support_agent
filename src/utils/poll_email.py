import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.search import GmailSearch
from agent.state import AgentState
from langchain_core.messages import HumanMessage

from utils.custom_gmail_tools import GmailMarkRead
from utils.run_workflow import run_workflow

load_dotenv()

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

# Capture time at last email and only search for newer emails
current_ts = int(asyncio.get_event_loop().time())

def search_email(toolkit: GmailToolkit):
    try:
        current_ts = int(asyncio.get_event_loop().time())
        search = GmailSearch(api_resource=toolkit.api_resource)
        # TODO: refactor query to filter by history api, not is:unread
        results = search.run({"query": "subject:support is:unread", "resource": "messages", "max_results": 1})
        
        if not results:
            return None
            # return state

        

        return results
    except Exception as e:
        print(f"Error while searching email: {e}")
        raise

async def poll_emails(toolkit: GmailToolkit):
    """Async polling loop — runs for the lifetime of the server."""
    print(f"Email polling started (interval: {POLL_INTERVAL_SECONDS}s)")
    while True:
        try:
            new_email = search_email(toolkit)
            if new_email:
                print(f"\n\nNew IT Support Request Email: {new_email}\n\n")
                print("New support email found — kicking off workflow...")
                # TODO: trigger LangGraph workflow with new_state
                workflow_run = asyncio.create_task(run_workflow(new_email), name="Run Workflow")
                
                try:
                    await workflow_run
                except asyncio.CancelledError:
                    pass

                # mark_as_read = GmailMarkRead(api_resource=toolkit.api_resource)
                # TODO: subscript the email id to mark it read from the raw results
                # mark_as_read.run({"message_id": email["id"]})
                # email = results[0]
                # message = HumanMessage(content=email.get("snippet", ""))
                # state.messages.append(message)


                # mark_as_read = GmailMarkRead(api_resource=toolkit.api_resource)
                # mark_as_read.run({"message_id": email["id"]})

                # print(f"{current_ts} Found email: {email.get('subject', '(no subject)')} from {email.get('sender', 'unknown')}.\nSnippet: {message.content[:50]}...")
            else:
                print("No new support emails.")
        except Exception as e:
            print(f"Error in polling loop: {e}")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)