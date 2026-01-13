"""Microsoft Graph API email service for mailbox monitoring."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmailAttachment:
    """Represents an email attachment."""

    name: str
    content_type: str
    content: bytes
    size: int


@dataclass
class IncomingEmail:
    """Represents an incoming email with attachments."""

    message_id: str
    sender: str
    subject: str
    received_at: datetime
    body: str
    attachments: list[EmailAttachment]
    case_id: Optional[str] = None  # Extracted from subject/body


class EmailService(ABC):
    """Abstract base class for email service."""

    @abstractmethod
    async def get_new_messages(
        self, since: Optional[datetime] = None
    ) -> list[IncomingEmail]:
        """Get new messages from the intake mailbox."""
        pass

    @abstractmethod
    async def mark_as_processed(self, message_id: str) -> None:
        """Mark a message as processed."""
        pass

    @abstractmethod
    async def get_attachments(self, message_id: str) -> list[EmailAttachment]:
        """Get attachments for a specific message."""
        pass


class MockEmailService(EmailService):
    """Mock email service for development/testing."""

    def __init__(self):
        """Initialize mock email service."""
        self._messages: dict[str, IncomingEmail] = {}
        self._processed: set[str] = set()
        self._setup_mock_messages()
        logger.info("MockEmailService initialized")

    def _setup_mock_messages(self):
        """Set up mock email messages for testing."""
        # Mock W-2 submission
        self._messages["mock-msg-001"] = IncomingEmail(
            message_id="mock-msg-001",
            sender="john.doe@example.com",
            subject="Document Submission - CASE-12345 - W-2",
            received_at=datetime.utcnow(),
            body="Please find attached my W-2 form for case CASE-12345.",
            attachments=[
                EmailAttachment(
                    name="w2_2025.pdf",
                    content_type="application/pdf",
                    content=b"Mock W-2 PDF content",
                    size=1024,
                )
            ],
            case_id="CASE-12345",
        )

        # Mock pay stub submission
        self._messages["mock-msg-002"] = IncomingEmail(
            message_id="mock-msg-002",
            sender="jane.smith@example.com",
            subject="Income Verification - CASE-67890",
            received_at=datetime.utcnow(),
            body="Attached is my recent pay stub for case CASE-67890.",
            attachments=[
                EmailAttachment(
                    name="paystub_dec2025.pdf",
                    content_type="application/pdf",
                    content=b"Mock pay stub PDF content",
                    size=2048,
                )
            ],
            case_id="CASE-67890",
        )

        # Mock utility bill submission
        self._messages["mock-msg-003"] = IncomingEmail(
            message_id="mock-msg-003",
            sender="bob.wilson@example.com",
            subject="Residency Proof - CASE-11111",
            received_at=datetime.utcnow(),
            body="Here is my utility bill for address verification. Case: CASE-11111",
            attachments=[
                EmailAttachment(
                    name="electric_bill.pdf",
                    content_type="application/pdf",
                    content=b"Mock utility bill PDF content",
                    size=512,
                )
            ],
            case_id="CASE-11111",
        )

    async def get_new_messages(
        self, since: Optional[datetime] = None
    ) -> list[IncomingEmail]:
        """Get new messages from mock mailbox."""
        new_messages = [
            msg
            for msg_id, msg in self._messages.items()
            if msg_id not in self._processed
        ]
        logger.info(f"Mock email service: {len(new_messages)} new messages")
        return new_messages

    async def mark_as_processed(self, message_id: str) -> None:
        """Mark a message as processed in mock store."""
        self._processed.add(message_id)
        logger.info(f"Mock email service: marked {message_id} as processed")

    async def get_attachments(self, message_id: str) -> list[EmailAttachment]:
        """Get attachments for a message from mock store."""
        message = self._messages.get(message_id)
        if message:
            return message.attachments
        return []

    def add_mock_message(self, message: IncomingEmail) -> None:
        """Add a mock message for testing."""
        self._messages[message.message_id] = message

    def clear_processed(self) -> None:
        """Clear processed status for testing."""
        self._processed.clear()


class GraphEmailService(EmailService):
    """Microsoft Graph API email service for production."""

    def __init__(self):
        """Initialize Graph API client."""
        settings = get_settings()
        self._client_id = settings.graph_client_id
        self._client_secret = settings.graph_client_secret
        self._tenant_id = settings.graph_tenant_id
        self._mailbox = settings.intake_mailbox
        self._client = None
        logger.info(f"GraphEmailService initialized for mailbox: {self._mailbox}")

    def _get_client(self):
        """Get or create Graph API client."""
        if self._client is None:
            try:
                from azure.identity import ClientSecretCredential
                from msgraph import GraphServiceClient

                credential = ClientSecretCredential(
                    tenant_id=self._tenant_id,
                    client_id=self._client_id,
                    client_secret=self._client_secret,
                )
                self._client = GraphServiceClient(credentials=credential)
            except ImportError:
                raise RuntimeError(
                    "msgraph-sdk and azure-identity packages not installed. "
                    "Run: pip install msgraph-sdk azure-identity"
                )
        return self._client

    async def get_new_messages(
        self, since: Optional[datetime] = None
    ) -> list[IncomingEmail]:
        """Get new messages from Graph API."""
        client = self._get_client()

        # Build filter query
        filter_query = "isRead eq false"
        if since:
            filter_query += f" and receivedDateTime ge {since.isoformat()}Z"

        try:
            messages = await client.users.by_user_id(
                self._mailbox
            ).messages.get(
                query_params={
                    "$filter": filter_query,
                    "$select": "id,sender,subject,receivedDateTime,body,hasAttachments",
                    "$orderby": "receivedDateTime desc",
                    "$top": 50,
                }
            )

            result = []
            for msg in messages.value if messages.value else []:
                attachments = []
                if msg.has_attachments:
                    attachments = await self.get_attachments(msg.id)

                # Extract case ID from subject/body
                case_id = self._extract_case_id(msg.subject, msg.body.content if msg.body else "")

                result.append(
                    IncomingEmail(
                        message_id=msg.id,
                        sender=msg.sender.email_address.address if msg.sender else "unknown",
                        subject=msg.subject or "",
                        received_at=msg.received_date_time or datetime.utcnow(),
                        body=msg.body.content if msg.body else "",
                        attachments=attachments,
                        case_id=case_id,
                    )
                )

            logger.info(f"Graph API: retrieved {len(result)} new messages")
            return result

        except Exception as e:
            logger.error(f"Failed to get messages from Graph API: {e}")
            raise

    async def mark_as_processed(self, message_id: str) -> None:
        """Mark a message as read in Graph API."""
        client = self._get_client()

        try:
            await client.users.by_user_id(
                self._mailbox
            ).messages.by_message_id(message_id).patch(
                {"isRead": True}
            )
            logger.info(f"Graph API: marked {message_id} as read")
        except Exception as e:
            logger.error(f"Failed to mark message as read: {e}")
            raise

    async def get_attachments(self, message_id: str) -> list[EmailAttachment]:
        """Get attachments for a message from Graph API."""
        client = self._get_client()

        try:
            attachments = await client.users.by_user_id(
                self._mailbox
            ).messages.by_message_id(message_id).attachments.get()

            result = []
            for att in attachments.value if attachments.value else []:
                # Only process file attachments
                if att.odata_type == "#microsoft.graph.fileAttachment":
                    import base64

                    content = base64.b64decode(att.content_bytes) if att.content_bytes else b""
                    result.append(
                        EmailAttachment(
                            name=att.name or "attachment",
                            content_type=att.content_type or "application/octet-stream",
                            content=content,
                            size=att.size or len(content),
                        )
                    )

            return result

        except Exception as e:
            logger.error(f"Failed to get attachments: {e}")
            raise

    def _extract_case_id(self, subject: str, body: str) -> Optional[str]:
        """Extract case ID from email subject or body."""
        import re

        # Look for patterns like CASE-12345 or Case #12345
        patterns = [
            r"CASE-(\d+)",
            r"Case[:\s#-]+(\d+)",
            r"case[:\s#-]+(\d+)",
        ]

        text = f"{subject} {body}"
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"CASE-{match.group(1)}"

        return None


def get_email_service() -> EmailService:
    """Get email service instance based on configuration."""
    settings = get_settings()
    if settings.use_mock_services:
        return MockEmailService()
    return GraphEmailService()
