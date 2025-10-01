# API Reference

This document describes the REST API endpoints available in the NYC Virtual Citizen Agent.

## Base URL

```
http://localhost:5000  (Development)
https://your-app.azurewebsites.net  (Production)
```

## Authentication

Currently, the API endpoints are publicly accessible. In production, consider implementing authentication based on your requirements.

## Search API

### Search Documents

Search for documents using text query.

**Endpoint:** `GET /api/search/documents`

**Parameters:**
- `query` (required): Search query string
- `maxResults` (optional): Maximum results to return (default: 5, max: 50)

**Example Request:**
```http
GET /api/search/documents?query=parking permit&maxResults=10
```

**Example Response:**
```json
{
  "query": "parking permit",
  "total_results": 3,
  "documents": [
    {
      "id": "1",
      "title": "Residential Parking Permit Application",
      "content": "How to apply for a residential parking permit...",
      "service_type": "permits",
      "category": "transportation",
      "relevance_score": 0.95,
      "last_updated": "2025-09-29 10:30:00"
    }
  ]
}
```

### Get Document by ID

Retrieve a specific document by its unique identifier.

**Endpoint:** `GET /api/search/documents/{id}`

**Parameters:**
- `id` (required): Document ID

**Example Request:**
```http
GET /api/search/documents/1
```

**Example Response:**
```json
{
  "id": "1",
  "title": "Residential Parking Permit Application",
  "content": "Complete guide to applying for residential parking permits...",
  "service_type": "permits",
  "category": "transportation",
  "last_updated": "2025-09-29 10:30:00"
}
```

### Search by Category

Search documents within a specific service category.

**Endpoint:** `GET /api/search/categories/{category}`

**Parameters:**
- `category` (required): Service category name
- `query` (optional): Additional search query within the category
- `maxResults` (optional): Maximum results to return (default: 10)

**Example Request:**
```http
GET /api/search/categories/transportation?query=parking&maxResults=5
```

**Example Response:**
```json
{
  "category": "transportation",
  "query": "parking",
  "total_results": 2,
  "documents": [
    {
      "id": "1",
      "title": "Parking Permit Information",
      "content": "Information about parking permits...",
      "service_type": "permits",
      "category": "transportation",
      "relevance_score": 0.88,
      "last_updated": "2025-09-29 10:30:00"
    }
  ]
}
```

### Get Available Categories

Retrieve list of all available service categories.

**Endpoint:** `GET /api/search/categories`

**Example Request:**
```http
GET /api/search/categories
```

**Example Response:**
```json
{
  "total_categories": 5,
  "categories": [
    "sanitation",
    "transportation",
    "permits",
    "health",
    "housing"
  ]
}
```

### Semantic Search

Perform AI-powered semantic search using natural language.

**Endpoint:** `GET /api/search/semantic`

**Parameters:**
- `query` (required): Natural language query
- `maxResults` (optional): Maximum results to return (default: 5)

**Example Request:**
```http
GET /api/search/semantic?query=I need help with trash pickup&maxResults=3
```

**Example Response:**
```json
{
  "semantic_query": "I need help with trash pickup",
  "total_results": 2,
  "documents": [
    {
      "id": "2",
      "title": "Waste Collection Schedule",
      "content": "Information about trash and recycling pickup...",
      "service_type": "waste_management",
      "category": "sanitation",
      "semantic_score": 0.92,
      "relevance_score": 0.89,
      "last_updated": "2025-09-29 09:15:00"
    }
  ]
}
```

### Recent Documents

Get recently updated documents.

**Endpoint:** `GET /api/search/recent`

**Parameters:**
- `daysBack` (optional): Number of days to look back (default: 7)
- `maxResults` (optional): Maximum results to return (default: 10)

**Example Request:**
```http
GET /api/search/recent?daysBack=30&maxResults=5
```

**Example Response:**
```json
{
  "days_back": 30,
  "cutoff_date": "2025-08-30 12:00:00",
  "total_results": 3,
  "documents": [
    {
      "id": "5",
      "title": "Updated Subway Service",
      "content": "Latest subway service updates...",
      "service_type": "transportation",
      "category": "transportation",
      "last_updated": "2025-09-28 14:20:00",
      "days_since_update": 1
    }
  ]
}
```

## Chat API

### Send Chat Message

Send a message to the AI assistant and receive a response with document sources.

**Endpoint:** `POST /api/chat/message`

**Request Body:**
```json
{
  "message": "How do I apply for a parking permit?"
}
```

**Example Response:**
```json
{
  "message": "To apply for a parking permit in NYC, you'll need to visit the local DMV office or apply online through the NYC.gov website. You'll need proof of residency, vehicle registration, and a valid driver's license. The application fee is $25 and permits are valid for one year.",
  "sources": [
    {
      "id": "1",
      "title": "Residential Parking Permit Application",
      "category": "transportation",
      "serviceType": "permits"
    }
  ],
  "timestamp": "2025-09-29T15:30:00Z"
}
```

### Get Chat History

Retrieve chat conversation history (currently returns empty array).

**Endpoint:** `GET /api/chat/history`

**Example Response:**
```json
{
  "messages": []
}
```

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "error": "Query parameter is required"
}
```

### 404 Not Found
```json
{
  "error": "Document with ID '999' not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An error occurred while searching documents"
}
```

## Response Headers

All responses include standard headers:
- `Content-Type: application/json`
- `Cache-Control: no-cache` (for dynamic content)

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production deployment based on your usage requirements.

## CORS Policy

CORS is configured to allow requests from any origin in development. Update CORS policy for production deployment.

## Data Models

### ServiceDocument
```typescript
interface ServiceDocument {
  id: string;
  title: string;
  content: string;
  service_type: string;
  category: string;
  relevance_score?: number;
  semantic_score?: number;
  last_updated: string; // ISO 8601 format
  days_since_update?: number;
}
```

### ChatMessage
```typescript
interface ChatMessageRequest {
  message: string;
}

interface ChatMessageResponse {
  message: string;
  sources: DocumentSource[];
  timestamp: string; // ISO 8601 format
}

interface DocumentSource {
  id: string;
  title: string;
  category: string;
  serviceType: string;
}
```

## Usage Examples

### JavaScript/Fetch
```javascript
// Search documents
const response = await fetch('/api/search/documents?query=parking permit');
const data = await response.json();

// Send chat message
const chatResponse = await fetch('/api/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'How do I get a business license?'
  })
});
const chatData = await chatResponse.json();
```

### cURL
```bash
# Search documents
curl "http://localhost:5000/api/search/documents?query=parking%20permit"

# Send chat message
curl -X POST "http://localhost:5000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get a business license?"}'
```

## SDK / Client Libraries

Currently, no official SDK is provided. The API is designed to be easily consumable by any HTTP client library.

---

This API reference covers all available endpoints in the NYC Virtual Citizen Agent. For implementation details, refer to the controller source code and development documentation.