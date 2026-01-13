import os
from typing import Annotated
from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

class DocumentRetrievalPlugin:
    def __init__(self):
        self.search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
        )

    @kernel_function(
        description="Search for information about city services",
        name="search_city_services"
    )
    def search_city_services(
        self, 
        query: Annotated[str, "The search query about city services"]
    ) -> str:
        """Search for relevant city service information."""
        try:
            # Perform search
            results = self.search_client.search(
                search_text=query,
                top=3,
                select=["title", "content", "service_type", "category"]
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "service_type": result.get("service_type", ""),
                    "category": result.get("category", "")
                })
            
            if not formatted_results:
                return "I couldn't find specific information about that service. Please try a different query or contact 311 for assistance."
            
            # Create response
            response = "Here's what I found about city services:\n\n"
            for i, result in enumerate(formatted_results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['content']}\n\n"
            
            return response
            
        except Exception as e:
            return f"I'm sorry, I encountered an error searching for that information. Please try again later."

    @kernel_function(
        description="Get specific service information by category",
        name="get_service_by_category"
    )
    def get_service_by_category(
        self, 
        category: Annotated[str, "The service category (sanitation, licensing, safety, recreation)"]
    ) -> str:
        """Get services filtered by category."""
        try:
            results = self.search_client.search(
                search_text="*",
                filter=f"category eq '{category}'",
                top=5,
                select=["title", "content", "service_type"]
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", "")
                })
            
            if not formatted_results:
                return f"No services found in the {category} category."
            
            response = f"Services in {category} category:\n\n"
            for i, result in enumerate(formatted_results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['content']}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving {category} services. Please try again."