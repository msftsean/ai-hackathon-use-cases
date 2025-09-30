# NYC Citizen Assistant - Sample Data

This folder contains sample datasets and documents used to populate the Azure AI Search index and test the Virtual Citizen Assistant.

## 📄 Files Included

### city_services_data.json
Comprehensive JSON file containing information about various NYC services:
- Trash and recycling schedules
- Permit application procedures  
- Emergency alert information
- Park hours and amenities
- Public transportation details

### emergency_alerts.json
Sample emergency alerts and notifications:
- Weather advisories
- Public safety alerts
- Service disruptions
- Health advisories

### permit_documents.json
Information about various NYC permits:
- Business permits
- Construction permits
- Event permits
- Street permits

### parks_and_recreation.json
NYC parks and recreation facility information:
- Park hours and locations
- Amenities and facilities
- Special programs and events
- Accessibility information

## 🔧 Usage

These files are used by the setup scripts to populate the Azure AI Search index:

```python
# Upload sample data to search index
python upload_sample_data.py
```

The data follows a consistent schema that matches the search index structure, ensuring accurate retrieval and consistent responses from the AI assistant.

## 📊 Data Schema

Each document in the search index contains:
- `id`: Unique identifier
- `service_type`: Category of service
- `title`: Human-readable title
- `content`: Full content text
- `category`: High-level category
- `last_updated`: Timestamp of last update

This structured approach enables efficient semantic search and accurate information retrieval for citizen queries.