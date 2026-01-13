"""
Test Setup and Environment Validation for Policy Compliance Checker
Ensures all dependencies are properly installed and configured.
"""
import sys
import importlib
import traceback
from typing import List, Tuple


def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False


def test_core_dependencies():
    """Test core Python dependencies"""
    print("\n📦 Testing core dependencies...")
    
    dependencies = [
        ("json", "JSON processing"),
        ("re", "Regular expressions"),
        ("os", "Operating system interface"),
        ("pathlib", "Path handling"),
        ("datetime", "Date and time"),
        ("dataclasses", "Data classes"),
        ("enum", "Enumerations"),
        ("typing", "Type hints"),
        ("asyncio", "Async operations")
    ]
    
    all_passed = True
    
    for module, description in dependencies:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {str(e)}")
            all_passed = False
    
    return all_passed


def test_semantic_kernel():
    """Test semantic kernel installation"""
    print("\n🧠 Testing Semantic Kernel...")
    
    try:
        import semantic_kernel
        from semantic_kernel import Kernel
        from semantic_kernel.functions import kernel_function
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        from semantic_kernel.contents.chat_history import ChatHistory
        
        print(f"✅ semantic-kernel {semantic_kernel.__version__} - Core functionality")
        print("✅ Kernel class imported")
        print("✅ kernel_function decorator imported")
        print("✅ AzureChatCompletion imported")
        print("✅ ChatHistory imported")
        
        # Test basic kernel creation
        kernel = Kernel()
        print("✅ Kernel instance created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ semantic-kernel - FAILED: {str(e)}")
        print("💡 Install with: pip install semantic-kernel==1.37.0")
        return False
    except Exception as e:
        print(f"❌ semantic-kernel - Error during testing: {str(e)}")
        return False


def test_azure_dependencies():
    """Test Azure SDK dependencies"""
    print("\n☁️ Testing Azure dependencies...")
    
    azure_modules = [
        ("azure.core", "Azure core library"),
        ("azure.identity", "Azure identity management"),
        ("azure.search.documents", "Azure Search Documents"),
        ("azure.ai.textanalytics", "Azure Text Analytics")
    ]
    
    all_passed = True
    
    for module, description in azure_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {str(e)}")
            all_passed = False
    
    return all_passed


def test_testing_dependencies():
    """Test testing framework dependencies"""
    print("\n🧪 Testing framework dependencies...")
    
    test_modules = [
        ("pytest", "Testing framework"),
        ("pytest_asyncio", "Async testing support"),
        ("pytest_mock", "Mocking support")
    ]
    
    all_passed = True
    
    for module, description in test_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - {description}")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {str(e)}")
            all_passed = False
    
    return all_passed


def test_project_structure():
    """Test project directory structure"""
    print("\n📁 Testing project structure...")
    
    import os
    from pathlib import Path
    
    required_dirs = [
        "src",
        "src/core",
        "src/plugins", 
        "tests",
        "assets",
        "assets/rule_templates",
        "assets/test_documents"
    ]
    
    all_passed = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ - Directory exists")
        else:
            print(f"❌ {dir_path}/ - Directory missing")
            all_passed = False
    
    return all_passed


def test_environment_variables():
    """Test environment variables for AI features"""
    print("\n🔧 Testing environment variables...")
    
    import os
    
    env_vars = [
        ("AZURE_OPENAI_DEPLOYMENT_NAME", "Azure OpenAI deployment name"),
        ("AZURE_OPENAI_ENDPOINT", "Azure OpenAI endpoint URL"),
        ("AZURE_OPENAI_API_KEY", "Azure OpenAI API key")
    ]
    
    ai_ready = True
    
    for var_name, description in env_vars:
        value = os.getenv(var_name)
        if value:
            # Don't print sensitive values
            if "KEY" in var_name or "SECRET" in var_name:
                print(f"✅ {var_name} - Set (value hidden)")
            else:
                print(f"✅ {var_name} - {value}")
        else:
            print(f"⚠️ {var_name} - Not set ({description})")
            ai_ready = False
    
    if ai_ready:
        print("✅ All Azure OpenAI credentials configured - AI features enabled")
    else:
        print("ℹ️ Azure OpenAI credentials not configured - AI features disabled")
    
    return True  # This is not critical for basic functionality


def test_sample_files():
    """Test that sample files are present"""
    print("\n📄 Testing sample files...")
    
    import os
    
    sample_files = [
        ("assets/test_documents/employee_code_of_conduct.md", "Sample policy document"),
        ("assets/rule_templates/legal_compliance_rules.json", "Sample compliance rules"),
        ("assets/rule_templates/consistency_rules.json", "Consistency rules")
    ]
    
    files_found = 0
    
    for file_path, description in sample_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
            files_found += 1
        else:
            print(f"⚠️ {file_path} - Missing ({description})")
    
    if files_found > 0:
        print(f"✅ {files_found}/{len(sample_files)} sample files found")
        return True
    else:
        print("⚠️ No sample files found - tests may be limited")
        return False


def run_all_tests():
    """Run all setup tests"""
    print("🚀 Policy Compliance Checker - Setup Validation")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Dependencies", test_core_dependencies),
        ("Semantic Kernel", test_semantic_kernel),
        ("Azure Dependencies", test_azure_dependencies),
        ("Testing Dependencies", test_testing_dependencies),
        ("Project Structure", test_project_structure),
        ("Environment Variables", test_environment_variables),
        ("Sample Files", test_sample_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed, None))
        except Exception as e:
            print(f"❌ {test_name} - CRASHED: {str(e)}")
            results.append((test_name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = []
    failed_tests = []
    
    for test_name, passed, error in results:
        if passed:
            passed_tests.append(test_name)
            print(f"✅ {test_name}")
        else:
            failed_tests.append((test_name, error))
            print(f"❌ {test_name}")
    
    print(f"\n🎯 Results: {len(passed_tests)}/{len(tests)} tests passed")
    
    if failed_tests:
        print("\n🔧 Failed Tests:")
        for test_name, error in failed_tests:
            print(f"   • {test_name}")
            if error:
                print(f"     Error: {error}")
    
    if len(passed_tests) == len(tests):
        print("\n🎉 ALL TESTS PASSED! Policy Compliance Checker is ready to use!")
        return True
    elif len(passed_tests) >= len(tests) - 2:  # Allow up to 2 non-critical failures
        print("\n✅ Core functionality ready! Some optional features may be limited.")
        return True
    else:
        print("\n❌ Critical issues found. Please resolve before using the application.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)