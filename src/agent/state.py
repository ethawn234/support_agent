# Email state schema for Support Agent per ServiceNow Incident Ticket
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Annotated
from langchain.messages import SystemMessage, HumanMessage, AIMessage

import operator

Category = Literal["network", "software", "hardware", "password_reset", "inquiry", "database"]
# The extent to which resolution of an incident can bear delay 
Urgency = Literal[1, 2, 3] # (1|2|3, High|Medium|Low)
# Sequence in which an incident needs to be resolved 
Priority = Literal[1, 2, 3, 4, 5] # "1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"
# The extent to which an incident affects the business
Impact = Literal[1, 2, 3]  # (1|2|3, High|Medium|Low)

class EmailState(BaseModel):
    sender_email: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Body content of the email")
    timestamp: str = Field(..., description="Timestamp of when the email was received")

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
    messages: Annotated[List[HumanMessage | AIMessage | SystemMessage], Field(default_factory=list, description="List of email interactions related to the user's issue"), operator.add]
    draft_ticket: Optional[ServiceNowIncident] = Field(None, description="Draft response being composed by the agent")
    comment_history: Annotated[Optional[List[str]], Field(default_factory=list, description="List of comments added to the incident ticket by the agent"), operator.add]
