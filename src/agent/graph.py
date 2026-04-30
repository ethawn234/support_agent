from langchain_google_community.gmail.search import GmailSearch
from langchain_google_community.gmail.utils import build_gmail_service
from langchain_openai import ChatOpenAI
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, END, START
from pydantic import SecretStr
import os

from agent.nodes import analyze_issue, analyze_issue, approval, classification, classification, create_ticket, input_guardrail, output_guardrail, send_slack_notification, output_guardrail
from agent.state import AgentState
from dotenv import load_dotenv

async def workflow():
    graph = StateGraph(AgentState)
    # add nodes
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("classification", classification)
    graph.add_node("analyze_issue", analyze_issue)
    graph.add_node("output_guardrail", output_guardrail)
    graph.add_node("approval", approval)
    graph.add_node("create_ticket", create_ticket)
    graph.add_node("send_slack_notification", send_slack_notification)

    # add edges
    graph.add_edge(START, "input_guardrail")
    graph.add_edge("input_guardrail", "classification")
    graph.add_edge("classification", "analyze_issue")
    graph.add_edge("analyze_issue", "output_guardrail")
    graph.add_edge("output_guardrail", "approval")
    graph.add_edge("approval", "create_ticket")
    graph.add_edge("create_ticket", "send_slack_notification")
    graph.add_edge("send_slack_notification", END)

    # compile graph and return    
    return graph.compile()
