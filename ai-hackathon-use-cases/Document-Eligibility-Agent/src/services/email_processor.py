"""
Email processing service for monitoring and processing eligibility documents
"""
import os
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.document_types import DocumentMetadata, DocumentType

# Try to import Azure services, fall back to mocks if not available
try:
    from azure.identity import ClientSecretCredential, DefaultAzureCredential
    from msgraph import GraphServiceClient  
    AZURE_SERVICES_AVAILABLE = True
except ImportError:
    # Mock classes for when Azure services aren't installed
    class ClientSecretCredential:
        def __init__(self, tenant_id, client_id, client_secret):
            pass
    
    class DefaultAzureCredential:
        def __init__(self):
            pass
    
    class GraphServiceClient:
        def __init__(self, credentials, scopes):
            pass
    
    AZURE_SERVICES_AVAILABLE = False


class EmailProcessorService:
    """Service for processing emails with eligibility document attachments"""
    
    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None):
        """
        Initialize email processor with Microsoft Graph credentials
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Application client ID  
            client_secret: Application client secret
        """
        self.logger = logging.getLogger(__name__)
        
        # Use provided credentials or fall back to environment variables
        self.tenant_id = tenant_id or os.getenv('MICROSOFT_GRAPH_TENANT_ID')
        self.client_id = client_id or os.getenv('MICROSOFT_GRAPH_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('MICROSOFT_GRAPH_CLIENT_SECRET')
        
        if all([self.tenant_id, self.client_id, self.client_secret]):
            self.credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        else:
            # Fall back to default credential chain
            self.credential = DefaultAzureCredential()
        
        self.client = GraphServiceClient(
            credentials=self.credential,
            scopes=['https://graph.microsoft.com/.default']
        )
        
        # Supported file types for document processing
        self.supported_file_types = {
            '.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.tiff', '.txt'
        }
    
    async def monitor_inbox(self, user_id: str = 'me', filter_subject: str = None) -> List[Dict[str, Any]]:
        """
        Monitor inbox for new emails with attachments
        
        Args:
            user_id: User ID or 'me' for current user
            filter_subject: Optional subject filter for eligibility emails
            
        Returns:
            List of email messages with attachments
        """
        try:
            self.logger.info(f"Monitoring inbox for user: {user_id}")
            
            # Build query filter
            query_filter = "hasAttachments eq true"
            if filter_subject:
                query_filter += f" and contains(subject, '{filter_subject}')"
            
            # Get messages with attachments
            messages = await self.client.users.by_user_id(user_id).messages.get(
                request_configuration=lambda q: q.query_parameters(
                    filter=query_filter,
                    select=['id', 'subject', 'sender', 'receivedDateTime', 'hasAttachments'],
                    top=50
                )
            )
            
            return messages.value if messages else []
            
        except Exception as e:
            self.logger.error(f"Error monitoring inbox: {str(e)}")
            return []
    
    async def get_message_attachments(self, user_id: str, message_id: str) -> List[DocumentMetadata]:
        """
        Get attachments from a specific email message
        
        Args:
            user_id: User ID or 'me' for current user
            message_id: Email message ID
            
        Returns:
            List of document metadata for eligible attachments
        """
        try:
            attachments = await self.client.users.by_user_id(user_id).messages.by_message_id(message_id).attachments.get()
            
            document_metadata = []
            for attachment in attachments.value if attachments else []:
                # Check if attachment is a supported document type
                file_name = attachment.name or "unknown"
                file_extension = os.path.splitext(file_name)[1].lower()
                
                if file_extension in self.supported_file_types:
                    metadata = DocumentMetadata(
                        document_id=attachment.id,
                        file_name=file_name,
                        file_size=attachment.size or 0,
                        mime_type=attachment.content_type or "application/octet-stream",
                        upload_timestamp=datetime.now(),
                        email_id=message_id
                    )
                    document_metadata.append(metadata)
                    
            return document_metadata
            
        except Exception as e:
            self.logger.error(f"Error getting attachments for message {message_id}: {str(e)}")
            return []
    
    async def download_attachment(self, user_id: str, message_id: str, attachment_id: str) -> Optional[bytes]:
        """
        Download attachment content
        
        Args:
            user_id: User ID or 'me' for current user
            message_id: Email message ID
            attachment_id: Attachment ID
            
        Returns:
            Attachment content as bytes or None if failed
        """
        try:
            attachment = await self.client.users.by_user_id(user_id).messages.by_message_id(message_id).attachments.by_attachment_id(attachment_id).get()
            
            if hasattr(attachment, 'content_bytes'):
                return attachment.content_bytes
            else:
                self.logger.warning(f"Attachment {attachment_id} has no content bytes")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading attachment {attachment_id}: {str(e)}")
            return None
    
    def classify_document_type(self, file_name: str, subject: str = "", body: str = "") -> DocumentType:
        """
        Classify document type based on filename and email content
        
        Args:
            file_name: Name of the attachment file
            subject: Email subject line
            body: Email body content
            
        Returns:
            Classified document type
        """
        file_name_lower = file_name.lower()
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # Income-related documents
        if any(keyword in file_name_lower for keyword in ['pay', 'stub', 'salary', 'income', 'tax', 'w2', '1099']):
            return DocumentType.INCOME_VERIFICATION
        
        # Medical documents
        if any(keyword in file_name_lower for keyword in ['medical', 'insurance', 'health', 'prescription', 'doctor']):
            return DocumentType.MEDICAL_RECORD
        
        # Utility bills
        if any(keyword in file_name_lower for keyword in ['utility', 'electric', 'gas', 'water', 'bill']):
            return DocumentType.UTILITY_BILL
        
        # Identity documents
        if any(keyword in file_name_lower for keyword in ['id', 'license', 'passport', 'ssn', 'social']):
            return DocumentType.IDENTITY_DOCUMENT
        
        # Housing documents
        if any(keyword in file_name_lower for keyword in ['lease', 'rent', 'mortgage', 'housing']):
            return DocumentType.HOUSING_DOCUMENT
            
        # Bank statements
        if any(keyword in file_name_lower for keyword in ['bank', 'statement', 'account']):
            return DocumentType.BANK_STATEMENT
        
        # Check email subject and body for additional context
        email_content = f"{subject_lower} {body_lower}"
        if any(keyword in email_content for keyword in ['snap', 'food', 'assistance', 'benefits']):
            if 'income' in email_content:
                return DocumentType.INCOME_VERIFICATION
            elif 'medical' in email_content:
                return DocumentType.MEDICAL_RECORD
        
        return DocumentType.UNKNOWN
    
    async def process_email_batch(self, user_id: str = 'me', batch_size: int = 10) -> List[DocumentMetadata]:
        """
        Process a batch of emails and extract document metadata
        
        Args:
            user_id: User ID or 'me' for current user
            batch_size: Number of emails to process in one batch
            
        Returns:
            List of document metadata from processed emails
        """
        try:
            # Get recent emails with attachments
            messages = await self.monitor_inbox(user_id)
            
            all_documents = []
            for message in messages[:batch_size]:
                # Get attachments for this message
                attachments = await self.get_message_attachments(user_id, message.id)
                
                # Classify document types and add email context
                for attachment in attachments:
                    attachment.email_id = message.id
                    attachment.sender_email = message.sender.email_address.address if message.sender else None
                    
                    # Classify document type based on filename and email content
                    doc_type = self.classify_document_type(
                        attachment.file_name,
                        message.subject or "",
                        ""  # Would need to get message body separately
                    )
                    
                    attachment.processing_notes.append(f"Classified as: {doc_type.value}")
                    all_documents.append(attachment)
            
            self.logger.info(f"Processed {len(all_documents)} documents from {len(messages)} emails")
            return all_documents
            
        except Exception as e:
            self.logger.error(f"Error processing email batch: {str(e)}")
            return []


# Mock implementation for testing without Graph API
class MockEmailProcessorService(EmailProcessorService):
    """Mock email processor for testing and development"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._doc_counter = 0  # Counter to ensure unique document IDs
        self.mock_emails = [
            {
                'id': '1',
                'subject': 'SNAP Application - Income Documentation',
                'sender': 'applicant@email.com',
                'attachments': ['pay_stub_march.pdf', 'bank_statement.pdf']
            },
            {
                'id': '2', 
                'subject': 'Medicaid Application Documents',
                'sender': 'patient@email.com',
                'attachments': ['insurance_card.jpg', 'medical_record.pdf']
            }
        ]
    
    async def monitor_inbox(self, user_id: str = 'me', filter_subject: str = None) -> List[Dict[str, Any]]:
        """Return mock email data"""
        class MockMessage:
            def __init__(self, email_data):
                self.id = email_data['id']
                self.subject = email_data['subject']
                self.sender = type('MockSender', (), {
                    'email_address': type('MockEmailAddress', (), {
                        'address': email_data['sender']
                    })()
                })()
                self.receivedDateTime = datetime.now().isoformat()
                self.hasAttachments = True
        
        return [MockMessage(email) for email in self.mock_emails]
    
    async def get_message_attachments(self, user_id: str, message_id: str) -> List[DocumentMetadata]:
        """Return mock attachment metadata"""
        mock_email = next((e for e in self.mock_emails if e['id'] == message_id), None)
        if not mock_email:
            return []
        
        attachments = []
        for i, filename in enumerate(mock_email['attachments']):
            self._doc_counter += 1
            metadata = DocumentMetadata(
                document_id=f"{message_id}_{i}_{self._doc_counter}",
                file_name=filename,
                file_size=1024 * (i + 1),
                mime_type="application/pdf" if filename.endswith('.pdf') else "image/jpeg",
                upload_timestamp=datetime.now(),
                email_id=message_id,
                sender_email=mock_email['sender']
            )
            attachments.append(metadata)
        
        return attachments
    
    async def download_attachment(self, user_id: str, message_id: str, attachment_id: str) -> Optional[bytes]:
        """Return mock attachment content"""
        return b"Mock attachment content for testing"