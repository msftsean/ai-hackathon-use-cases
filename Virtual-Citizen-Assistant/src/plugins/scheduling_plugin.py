import os
from typing import Annotated
from semantic_kernel.functions import kernel_function
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

load_dotenv()

class SchedulingPlugin:
    def __init__(self):
        # In a real implementation, this would connect to a scheduling API
        # For demo purposes, we'll use mock data
        self.mock_appointments = [
            {
                "id": "1",
                "service": "Building Permit Application",
                "date": "2024-01-15",
                "time": "10:00 AM",
                "status": "available"
            },
            {
                "id": "2", 
                "service": "Business License Renewal",
                "date": "2024-01-16",
                "time": "2:00 PM",
                "status": "available"
            }
        ]

    @kernel_function(
        description="Check available appointment slots for city services",
        name="check_availability"
    )
    def check_availability(
        self,
        service: Annotated[str, "The type of service to schedule (e.g., 'building permit', 'business license')"]
    ) -> str:
        """Check available appointment slots for a specific service."""
        try:
            # Filter available appointments for the requested service
            available_slots = [
                apt for apt in self.mock_appointments 
                if service.lower() in apt["service"].lower() and apt["status"] == "available"
            ]
            
            if not available_slots:
                return f"I'm sorry, there are currently no available appointments for {service}. Please call 311 or check back later."
            
            response = f"Available appointments for {service}:\n\n"
            for slot in available_slots:
                response += f"📅 {slot['date']} at {slot['time']}\n"
                response += f"   Service: {slot['service']}\n"
                response += f"   ID: {slot['id']}\n\n"
            
            response += "To book an appointment, please call 311 or visit our online portal."
            return response
            
        except Exception as e:
            return f"I'm sorry, I encountered an error checking appointment availability. Please try again later."

    @kernel_function(
        description="Get general information about scheduling city services",
        name="scheduling_info"
    )
    def scheduling_info(
        self,
        query: Annotated[str, "Question about scheduling or appointments"]
    ) -> str:
        """Provide information about scheduling city services."""
        try:
            # Common scheduling information
            info_responses = {
                "hours": "City services are available Monday-Friday, 8:00 AM - 5:00 PM. Some services may have extended hours.",
                "online": "Many services can be scheduled online at our city portal. Visit [city website] or call 311 for assistance.",
                "requirements": "Please bring valid ID and any required documentation. Specific requirements vary by service type.",
                "cancellation": "Appointments can be cancelled up to 24 hours in advance without penalty. Call 311 to cancel or reschedule.",
                "contact": "For scheduling assistance, call 311 or visit our main office at City Hall during business hours."
            }
            
            query_lower = query.lower()
            
            # Return relevant information based on query
            for key, response in info_responses.items():
                if key in query_lower:
                    return response
            
            # Default response
            return """Here's general information about scheduling city services:

📞 **Contact**: Call 311 for all scheduling needs
🕐 **Hours**: Monday-Friday, 8:00 AM - 5:00 PM  
💻 **Online**: Many services available online at city portal
📋 **Requirements**: Bring valid ID and required documentation
⏰ **Cancellations**: Cancel up to 24 hours in advance

For specific service requirements or to schedule an appointment, please call 311."""
            
        except Exception as e:
            return f"I'm sorry, I encountered an error retrieving scheduling information. Please call 311 for assistance."

    @kernel_function(
        description="List all available city services that can be scheduled",
        name="list_schedulable_services"
    )
    def list_schedulable_services(self) -> str:
        """List all city services that can be scheduled for appointments."""
        try:
            services = [
                "Building Permits",
                "Business License Applications", 
                "Zoning Consultations",
                "Building Inspections",
                "Planning Department Meetings",
                "Tax Assessment Appeals",
                "Parking Permit Applications",
                "Special Event Permits",
                "Public Records Requests",
                "Code Enforcement Consultations"
            ]
            
            response = "📋 **City Services Available for Scheduling:**\n\n"
            for i, service in enumerate(services, 1):
                response += f"{i}. {service}\n"
            
            response += "\n📞 To schedule any of these services, call 311 or visit our online portal."
            response += "\n💡 Some services may require advance scheduling or have specific requirements."
            
            return response
            
        except Exception as e:
            return "I'm sorry, I encountered an error retrieving the service list. Please call 311 for current available services."