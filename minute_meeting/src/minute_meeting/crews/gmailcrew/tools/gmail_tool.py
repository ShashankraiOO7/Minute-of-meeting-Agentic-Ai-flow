# gmail_tool.py
from __future__ import annotations
import os
from typing import Literal, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ValidationError

from .gmail_utility import (
    authenticate_gmail,
    create_message,
    create_draft,
    send_message,
)

# ------------------------------------------------------------------ #
# Pydantic schema for CrewAI arguments
# ------------------------------------------------------------------ #
class GmailToolInput(BaseModel):
    body: str = Field(..., description="Body of the e-mail.")
    mode: Literal["draft", "send"] = Field(
        default="draft",
        description="'draft' ➜ save draft, 'send' ➜ send immediately.",
    )


# ------------------------------------------------------------------ #
# CrewAI Tool definition
# ------------------------------------------------------------------ #
class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = (
        "Create a Gmail draft or send an e-mail.\n"
        "Requires env vars GMAIL_SENDER & GMAIL_RECIPIENT and a credentials.json/token.json pair.\n"
        "Optional env var GMAIL_CREDENTIALS lets you point to the creds file explicitly."
    )
    args_schema: Type[BaseModel] = GmailToolInput

    # CrewAI synchronous runner
    def _run(self, body: str, mode: str = "draft") -> str:  # pylint: disable=arguments-differ
        try:
            sender = os.getenv("GMAIL_SENDER")
            recipient = os.getenv("GMAIL_RECIPIENT")
            if not sender or not recipient:
                raise ValueError(
                    "Environment variables GMAIL_SENDER and/or GMAIL_RECIPIENT are missing."
                )

            service = authenticate_gmail()
            subject = "Meeting Minutes"
            message = create_message(sender, recipient, subject, body)

            if mode == "draft":
                draft = create_draft(service, "me", message)
                return f"✅ Draft created (id: {draft['id']})."

            if mode == "send":
                sent = send_message(service, "me", message)
                return f"✅ Email sent (id: {sent['id']})."

            raise ValidationError("mode must be 'draft' or 'send'.")

        except Exception as exc:  # pylint: disable=broad-except
            return f"❌ GmailTool error: {exc}"


