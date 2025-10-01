"""
Virtual Citizen Assistant - Main Application
Updated for Semantic Kernel 1.37.0 and Pydantic v2 compatibility
"""
import asyncio
import os
from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from src.plugins.document_retrieval_plugin import DocumentRetrievalPlugin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VirtualCitizenAssistant:
    def __init__(self):
        self.kernel: Optional[Kernel] = None
        self.chat_history = ChatHistory()
        
    async def initialize(self):
        """Initialize the kernel and plugins"""
        print("Initializing Virtual Citizen Assistant...")
        
        # Create kernel
        self.kernel = Kernel()
        
        # Add Azure OpenAI service
        chat_service = AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        self.kernel.add_service(chat_service)
        
        # Add document retrieval plugin
        document_plugin = DocumentRetrievalPlugin()
        self.kernel.add_plugin(document_plugin, plugin_name="DocumentRetrieval")
        
        # Add scheduling plugin
        from src.plugins.scheduling_plugin import SchedulingPlugin
        scheduling_plugin = SchedulingPlugin()
        self.kernel.add_plugin(scheduling_plugin, plugin_name="Scheduling")
        
        print("✅ Virtual Citizen Assistant initialized successfully!")
        print("   - DocumentRetrieval plugin loaded")
        print("   - Scheduling plugin loaded")
        
    async def chat(self, user_message: str) -> str:
        """Process a user message and return a response"""
        if not self.kernel:
            raise RuntimeError("Assistant not initialized. Call initialize() first.")
        
        # Add user message to history
        self.chat_history.add_user_message(user_message)
        
        # Create a prompt that includes available functions
        system_prompt = """
You are a helpful virtual assistant for city services. You can help citizens with:
1. Finding information about city services (DocumentRetrieval plugin)
2. Getting service information by category (DocumentRetrieval plugin)
3. Checking appointment availability (Scheduling plugin)
4. Getting scheduling information (Scheduling plugin)
5. Answering general questions about municipal services

Available plugins and functions:
- DocumentRetrieval.search_city_services: for general service searches
- DocumentRetrieval.get_service_by_category: for category-specific searches
- Scheduling.check_availability: check appointment slots
- Scheduling.scheduling_info: general scheduling information
- Scheduling.list_schedulable_services: list all services that can be scheduled

Available service categories: sanitation, licensing, safety, recreation

Be helpful, friendly, and informative.
"""
        
        # Get chat completion with function calling
        response = await self.kernel.invoke_prompt(
            function_name="chat",
            plugin_name="chat",
            prompt=f"{system_prompt}\n\nUser: {user_message}\nAssistant:",
        )
        
        # Add assistant response to history
        assistant_response = str(response)
        self.chat_history.add_assistant_message(assistant_response)
        
        return assistant_response
    
    def get_chat_history(self) -> list:
        """Get the current chat history"""
        return [{"role": msg.role.value, "content": msg.content} for msg in self.chat_history.messages]

async def main():
    """Main function for testing the assistant"""
    assistant = VirtualCitizenAssistant()
    
    try:
        await assistant.initialize()
        
        print("\n" + "="*50)
        print("Virtual Citizen Assistant is ready!")
        print("You can now ask questions about city services.")
        print("Type 'quit' to exit.")
        print("="*50 + "\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Assistant: Goodbye! Have a great day!")
                break
            
            if not user_input:
                continue
            
            try:
                response = await assistant.chat(user_input)
                print(f"Assistant: {response}")
            except Exception as e:
                print(f"Assistant: I'm sorry, I encountered an error: {e}")
                
    except Exception as e:
        print(f"Failed to initialize assistant: {e}")
        print("Please check your environment variables:")
        print("- AZURE_OPENAI_ENDPOINT")
        print("- AZURE_OPENAI_API_KEY")
        print("- AZURE_OPENAI_DEPLOYMENT_NAME")
        print("- AZURE_SEARCH_ENDPOINT")
        print("- AZURE_SEARCH_KEY")
        print("- AZURE_SEARCH_INDEX")

if __name__ == "__main__":
    asyncio.run(main())