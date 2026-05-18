# Email state schema for Support Agent per ServiceNow Incident Ticket
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Annotated
from langchain.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import MessagesState
from langchain_google_community import GmailToolkit

import operator

Category = Literal["network", "software", "hardware", "password_reset", "inquiry", "database"]
# The extent to which resolution of an incident can bear delay 
Urgency = Literal[1, 2, 3] # (1|2|3, High|Medium|Low)
# Sequence in which an incident needs to be resolved 
Priority = Literal[1, 2, 3, 4, 5] # "1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"
# The effect of an issue on the business
Impact = Literal[1, 2, 3] # 1 - High, 2 - Medium, 3 - Low

Breaker_State = Literal["OPEN", "CLOSED", "HALF-OPEN", "DEGRADED"]
class EmailClassification(BaseModel):
    intent: str = Field(..., description="The intent of the email (e.g., password reset, software issue, hardware issue)")
    urgency: Urgency = Field(..., description="Urgency level of the issue")
    category: Category = Field(..., description="Category of the issue")
    analysis: str = Field(..., description="Agent's analysis and recommendation")
    priority: Priority = Field(..., description="Severity of the issue")
    impact: Impact = Field(..., description="The effect of an issue on the business")
    needs_info: Optional[str] = Field(None, description="List of additional information user must provide to process request")
class ServiceNowIncident(BaseModel):
    short_description: str = Field(..., description="Short description of the incident")
    description: str = Field(..., description="Detailed description of the incident")
    priority: Priority = Field(..., description="Priority level of the incident")
    category: Category = Field(..., description="Category of the incident (e.g., Software, Hardware, Network)")
    caller_id: Optional[str] = Field(None, description="Identifier for the caller (user reporting the incident)")
    impact: Impact = Field(..., description="The effect of an issue on the business")
class AgentState(BaseModel):
    draft_ticket: Optional[ServiceNowIncident] = Field(None, description="Draft response being composed by the agent")
    classification: Optional[EmailClassification] = Field(None, description="LLMs classification of user's issue")
    # breaker_state: Breaker_State = Field(description="state of any risky operation")
    is_valid_req: bool | None
    email_content: str | None
    id: str | None
    raw_email: List[dict] | None
    messages: List[SystemMessage|HumanMessage|AIMessage|ToolMessage] | None
    toolkit: GmailToolkit