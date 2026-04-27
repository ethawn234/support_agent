from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from langchain_google_community.gmail.base import GmailBaseTool


class MarkReadArgsSchema(BaseModel):
    """Input schema for `GmailMarkRead`."""

    message_id: str = Field(
        ...,
        description="The unique ID of the email message to mark as read.",
    )


class GmailMarkRead(GmailBaseTool):
    """Tool that marks a Gmail message as read."""

    name: str = "mark_gmail_as_read"

    description: str = (
        "Use this tool to mark an email message as read in Gmail."
        " Input should be the unique message ID."
    )

    args_schema: Type[MarkReadArgsSchema] = MarkReadArgsSchema

    def _run(
        self,
        message_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        # POST https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{id}/modify
        query = (
            self.api_resource.users()
            .messages()
            .modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]})
        )
        result = query.execute()
        return f"Message marked as read. Message Id: {result['id']}"