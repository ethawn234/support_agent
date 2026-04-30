# Email state schema for Support Agent per ServiceNow Incident Ticket
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Annotated
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import MessagesState

import operator

Category = Literal["network", "software", "hardware", "password_reset", "inquiry", "database"]
# The extent to which resolution of an incident can bear delay 
Urgency = Literal[1, 2, 3] # (1|2|3, High|Medium|Low)
# Sequence in which an incident needs to be resolved 
Priority = Literal[1, 2, 3, 4, 5] # "1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"
# The extent to which an incident affects the business
Impact = Literal[1, 2, 3]  # (1|2|3, High|Medium|Low)

Breaker_State = Literal["OPEN", "CLOSED", "HALF-OPEN"]
class EmailClassification(BaseModel):
    intent: str = Field(..., description="The intent of the email (e.g., password reset, software issue, hardware issue)")
    urgency: Urgency = Field(..., description="Urgency level of the issue")
    category: Category = Field(..., description="Category of the issue")
    summary: str = Field(..., description="A brief summary of the issue described in the email")
class ServiceNowIncident(BaseModel):
    short_description: str = Field(..., description="Short description of the incident")
    description: str = Field(..., description="Detailed description of the incident")
    priority: Priority = Field(..., description="Priority level of the incident")
    category: Category = Field(..., description="Category of the incident (e.g., Software, Hardware, Network)")
    caller_id: Optional[str] = Field(None, description="Identifier for the caller (user reporting the incident)")
class AgentState(BaseModel):
    draft_ticket: Optional[ServiceNowIncident] = Field(None, description="Draft response being composed by the agent")
    classification: Optional[EmailClassification] = Field(None, description="LLMs classification of user's issue")
    # breaker_state: Breaker_State = Field(description="state of any risky operation")
    is_valid_req: bool | None
    email_content: str | None
    id: str | None
    raw_email: List[dict] | None
    messages: List[SystemMessage|HumanMessage|AIMessage] | None