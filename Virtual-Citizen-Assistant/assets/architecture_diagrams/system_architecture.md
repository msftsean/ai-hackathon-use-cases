# Virtual Citizen Assistant - Architecture Overview

## System Architecture Diagram

```mermaid
graph TD
    A[Citizen Query] --> B[Azure Web App]
    B --> C[Semantic Kernel Planner]
    C --> D[Plugin Orchestration]
    
    D --> E[Document Retrieval Plugin]
    D --> F[Scheduling Plugin]
    D --> G[Emergency Alerts Plugin]
    
    E --> H[Azure AI Search]
    F --> I[City APIs]
    G --> J[Notification Service]
    
    H --> K[City Knowledge Base]
    I --> L[Scheduling Systems]
    J --> M[Emergency Systems]
    
    C --> N[Response Generation]
    N --> O[Citizen Response]
```

## Component Flow Diagram

```mermaid
sequenceDiagram
    participant Citizen
    participant WebApp
    participant SemanticKernel
    participant AISearch
    participant CityAPIs
    
    Citizen->>WebApp: Ask query
    WebApp->>SemanticKernel: Process query
    SemanticKernel->>AISearch: Search documents
    AISearch-->>SemanticKernel: Return results
    SemanticKernel->>CityAPIs: Get real-time data
    CityAPIs-->>SemanticKernel: Return data
    SemanticKernel->>WebApp: Generate response
    WebApp->>Citizen: Provide answer
```

## Plugin Architecture

```mermaid
graph LR
    A[Semantic Kernel] --> B[Document Retrieval Plugin]
    A --> C[Scheduling Plugin]  
    A --> D[Alerts Plugin]
    
    B --> E[Vector Search]
    B --> F[Content Filtering]
    
    C --> G[Address Parsing]
    C --> H[Schedule Calculation]
    
    D --> I[Alert Classification]
    D --> J[Location Matching]
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Azure Cloud"
        A[Azure Web App]
        B[Azure AI Search]
        C[Azure OpenAI]
        D[Azure Key Vault]
        E[Application Insights]
    end
    
    subgraph "External Services"
        F[City APIs]
        G[Emergency Services]
        H[MTA APIs]
    end
    
    subgraph "Development"
        I[GitHub Codespaces]
        J[GitHub Repository]
    end
    
    A <--> B
    A <--> C
    A <--> D
    A --> E
    A <--> F
    A <--> G
    A <--> H
    I <--> J
    J --> A
```

This architecture ensures:
- **Scalability**: Azure Web App can scale based on demand
- **Security**: All secrets managed through Azure Key Vault
- **Monitoring**: Application Insights for performance tracking
- **Flexibility**: Plugin-based architecture for easy extensions
- **Reliability**: Multiple fallback mechanisms for service continuity