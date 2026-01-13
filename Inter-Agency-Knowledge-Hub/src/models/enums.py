"""Enumerations for Inter-Agency Knowledge Hub."""

from enum import Enum


class Agency(str, Enum):
    """New York State agencies in the knowledge hub."""

    DMV = "dmv"  # Department of Motor Vehicles
    DOL = "dol"  # Department of Labor
    OTDA = "otda"  # Office of Temporary and Disability Assistance
    DOH = "doh"  # Department of Health
    OGS = "ogs"  # Office of General Services

    @property
    def full_name(self) -> str:
        """Get the full agency name."""
        names = {
            "dmv": "Department of Motor Vehicles",
            "dol": "Department of Labor",
            "otda": "Office of Temporary and Disability Assistance",
            "doh": "Department of Health",
            "ogs": "Office of General Services",
        }
        return names[self.value]

    @property
    def index_name(self) -> str:
        """Get the Azure AI Search index name for this agency."""
        return f"agency-docs-{self.value}"


class DocumentClassification(str, Enum):
    """Document classification levels."""

    PUBLIC = "public"  # Available to all users
    INTERNAL = "internal"  # Available to agency staff
    RESTRICTED = "restricted"  # Available to agency managers
    CONFIDENTIAL = "confidential"  # Available to agency admins only

    @property
    def access_level(self) -> int:
        """Get numeric access level (higher = more restricted)."""
        levels = {
            "public": 0,
            "internal": 1,
            "restricted": 2,
            "confidential": 3,
        }
        return levels[self.value]


class RelationshipType(str, Enum):
    """Types of relationships between documents."""

    SIMILAR_TOPIC = "similar_topic"  # Documents on similar topics
    DEPENDENCY = "dependency"  # One document depends on another
    SUPERSEDES = "supersedes"  # Document replaces an older version
    CONFLICT = "conflict"  # Documents have conflicting information
    RELATED = "related"  # General relationship


class ReviewStatus(str, Enum):
    """Status of human review for flagged queries."""

    PENDING = "pending"  # Awaiting review
    APPROVED = "approved"  # Approved for delivery
    MODIFIED = "modified"  # Modified before delivery
    REJECTED = "rejected"  # Query rejected


class ActionType(str, Enum):
    """Types of actions logged in audit trail."""

    SEARCH = "search"  # User performed a search
    VIEW = "view"  # User viewed a document
    EXPORT = "export"  # User exported search results
    CROSS_REFERENCE = "cross_reference"  # User viewed cross-references
