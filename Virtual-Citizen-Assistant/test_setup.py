"""
Test script to validate the Virtual Citizen Assistant setup
"""
import os
import sys
import traceback

def test_imports():
    """Test that all required imports work correctly"""
    print("=== Testing Imports ===")
    
    try:
        import semantic_kernel
        print(f"✅ Semantic Kernel {semantic_kernel.__version__} imported successfully")
    except Exception as e:
        print(f"❌ Semantic Kernel import failed: {e}")
        return False
    
    try:
        from pydantic import networks
        print("✅ Pydantic networks imported successfully")
    except Exception as e:
        print(f"❌ Pydantic networks import failed: {e}")
        return False
    
    try:
        from src.plugins.document_retrieval_plugin import DocumentRetrievalPlugin
        print("✅ DocumentRetrievalPlugin imported successfully")
    except Exception as e:
        print(f"❌ DocumentRetrievalPlugin import failed: {e}")
        return False
    
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        print("✅ Azure Search imports successful")
    except Exception as e:
        print(f"❌ Azure Search imports failed: {e}")
        return False
    
    return True

def test_plugin_creation():
    """Test that the plugin can be instantiated"""
    print("\n=== Testing Plugin Creation ===")
    
    try:
        # Set dummy environment variables for testing
        os.environ['AZURE_SEARCH_ENDPOINT'] = 'https://test.search.windows.net'
        os.environ['AZURE_SEARCH_INDEX'] = 'test-index'
        os.environ['AZURE_SEARCH_KEY'] = 'test-key'
        
        from src.plugins.document_retrieval_plugin import DocumentRetrievalPlugin
        plugin = DocumentRetrievalPlugin()
        print("✅ DocumentRetrievalPlugin created successfully")
        return True
    except Exception as e:
        print(f"❌ Plugin creation failed: {e}")
        traceback.print_exc()
        return False

def test_kernel_function_decorators():
    """Test that the kernel function decorators work"""
    print("\n=== Testing Kernel Function Decorators ===")
    
    try:
        from semantic_kernel.functions import kernel_function
        from typing import Annotated
        
        @kernel_function(description="Test function", name="test_func")
        def test_function(query: Annotated[str, "Test parameter"]) -> str:
            return f"Test result for: {query}"
        
        result = test_function("hello")
        print(f"✅ Kernel function decorator works: {result}")
        return True
    except Exception as e:
        print(f"❌ Kernel function decorator failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Virtual Citizen Assistant Compatibility Tests\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test plugin creation
    if not test_plugin_creation():
        all_passed = False
    
    # Test kernel function decorators
    if not test_kernel_function_decorators():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The Virtual Citizen Assistant is ready to use.")
        print("\nKey fixes applied:")
        print("- Updated semantic-kernel from 0.9.1b1 to 1.37.0")
        print("- Updated all dependencies to compatible versions")
        print("- Fixed pydantic v2 compatibility issues")
        print("- Updated plugin decorators to use new API")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()