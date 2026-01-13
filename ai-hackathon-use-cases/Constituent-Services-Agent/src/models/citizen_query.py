# NYC Citizen Assistant - Query Models

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QueryType(Enum):
    """Types of citizen queries."""
    TRASH_PICKUP = "trash_pickup"
    RECYCLING = "recycling"
    PERMITS = "permits"
    EMERGENCY_ALERTS = "emergency_alerts"
    PARK_INFO = "park_info"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"

class Priority(Enum):
    """Query priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class CitizenQuery:
    """Represents a citizen's query to the assistant."""
    
    query_id: str
    user_message: str
    session_id: str
    timestamp: datetime
    query_type: QueryType = QueryType.UNKNOWN
    priority: Priority = Priority.MEDIUM
    
    # Extracted entities
    address: Optional[str] = None
    service_type: Optional[str] = None
    location: Optional[str] = None
    
    # Context
    conversation_history: Optional[List[Dict[str, str]]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    
    # Response data
    response: Optional[str] = None
    plugins_used: Optional[List[str]] = None
    response_time_ms: Optional[int] = None
    confidence_score: Optional[float] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.conversation_history is None:
            self.conversation_history = []
        
        if self.user_preferences is None:
            self.user_preferences = {}
        
        if self.plugins_used is None:
            self.plugins_used = []
        
        # Auto-detect query type based on keywords
        self.query_type = self._detect_query_type()
        
        # Set priority based on query type
        self.priority = self._determine_priority()
    
    def _detect_query_type(self) -> QueryType:
        """Detect query type based on message content."""
        message_lower = self.user_message.lower()
        
        # Emergency-related keywords
        emergency_keywords = ['emergency', 'alert', 'urgent', 'disaster', 'evacuation']
        if any(keyword in message_lower for keyword in emergency_keywords):
            return QueryType.EMERGENCY_ALERTS
        
        # Trash/waste keywords
        trash_keywords = ['trash', 'garbage', 'pickup', 'collection', 'bin', 'waste']
        if any(keyword in message_lower for keyword in trash_keywords):
            return QueryType.TRASH_PICKUP
        
        # Recycling keywords
        recycling_keywords = ['recycl', 'recycle', 'blue bin', 'compost']
        if any(keyword in message_lower for keyword in recycling_keywords):
            return QueryType.RECYCLING
        
        # Permit keywords
        permit_keywords = ['permit', 'license', 'application', 'business', 'construction']
        if any(keyword in message_lower for keyword in permit_keywords):
            return QueryType.PERMITS
        
        # Park keywords
        park_keywords = ['park', 'playground', 'recreation', 'hours', 'central park', 'prospect park']
        if any(keyword in message_lower for keyword in park_keywords):
            return QueryType.PARK_INFO
        
        return QueryType.GENERAL_INFO
    
    def _determine_priority(self) -> Priority:
        """Determine priority based on query type and content."""
        if self.query_type == QueryType.EMERGENCY_ALERTS:
            return Priority.URGENT
        
        urgent_keywords = ['urgent', 'emergency', 'immediate', 'asap']
        if any(keyword in self.user_message.lower() for keyword in urgent_keywords):
            return Priority.HIGH
        
        if self.query_type in [QueryType.PERMITS, QueryType.GENERAL_INFO]:
            return Priority.MEDIUM
        
        return Priority.LOW
    
    def extract_address(self) -> Optional[str]:
        """Extract address from the query message."""
        import re
        
        # Simple regex patterns for NYC addresses
        patterns = [
            r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|place|pl|drive|dr)\b',
            r'\b\d+\s+\w+\s+\w+\b'  # Simple pattern like "123 Main Street"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.user_message, re.IGNORECASE)
            if match:
                self.address = match.group().strip()
                return self.address
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary for serialization."""
        return {
            'query_id': self.query_id,
            'user_message': self.user_message,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'query_type': self.query_type.value,
            'priority': self.priority.value,
            'address': self.address,
            'service_type': self.service_type,
            'location': self.location,
            'response': self.response,
            'plugins_used': self.plugins_used,
            'response_time_ms': self.response_time_ms,
            'confidence_score': self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CitizenQuery':
        """Create query from dictionary."""
        return cls(
            query_id=data['query_id'],
            user_message=data['user_message'],
            session_id=data['session_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            query_type=QueryType(data.get('query_type', QueryType.UNKNOWN.value)),
            priority=Priority(data.get('priority', Priority.MEDIUM.value)),
            address=data.get('address'),
            service_type=data.get('service_type'),
            location=data.get('location'),
            response=data.get('response'),
            plugins_used=data.get('plugins_used', []),
            response_time_ms=data.get('response_time_ms'),
            confidence_score=data.get('confidence_score')
        )

@dataclass
class QueryResponse:
    """Represents the response to a citizen query."""
    
    query_id: str
    response_text: str
    confidence_score: float
    plugins_used: List[str]
    processing_time_ms: int
    sources: Optional[List[Dict[str, str]]] = None
    follow_up_suggestions: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        
        if self.follow_up_suggestions is None:
            self.follow_up_suggestions = []
    
    def add_source(self, title: str, url: str, snippet: str = ""):
        """Add a source reference to the response."""
        self.sources.append({
            'title': title,
            'url': url,
            'snippet': snippet
        })
    
    def add_follow_up(self, suggestion: str):
        """Add a follow-up question suggestion."""
        self.follow_up_suggestions.append(suggestion)

# Helper functions for query processing

def classify_query_intent(message: str) -> QueryType:
    """Classify the intent of a user message."""
    query = CitizenQuery(
        query_id="temp",
        user_message=message,
        session_id="temp",
        timestamp=datetime.now()
    )
    return query.query_type

def extract_entities(message: str) -> Dict[str, Optional[str]]:
    """Extract entities from a user message."""
    query = CitizenQuery(
        query_id="temp",
        user_message=message,
        session_id="temp", 
        timestamp=datetime.now()
    )
    
    return {
        'address': query.extract_address(),
        'query_type': query.query_type.value,
        'priority': query.priority.value
    }