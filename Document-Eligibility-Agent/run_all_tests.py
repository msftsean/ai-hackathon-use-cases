"""
Comprehensive test runner for Document Eligibility Agent
"""
import sys
import os
import subprocess
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tests.test_setup import run_setup_tests
from tests.test_core_components import run_core_component_tests
from tests.test_plugins import run_plugin_tests
from tests.test_integration import run_integration_tests


def run_all_tests():
    """Run all test suites for Document Eligibility Agent"""
    print("🚀 Document Eligibility Agent - Comprehensive Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    test_results = {}
    
    # Test Suite 1: Setup Validation
    print("📋 PHASE 1: Setup and Configuration Tests")
    print("-" * 50)
    try:
        test_results['setup'] = run_setup_tests()
    except Exception as e:
        print(f"❌ Setup tests failed with exception: {e}")
        test_results['setup'] = False
    
    print()
    
    # Test Suite 2: Core Components
    print("📋 PHASE 2: Core Component Tests")
    print("-" * 50)
    try:
        test_results['core_components'] = run_core_component_tests()
    except Exception as e:
        print(f"❌ Core component tests failed with exception: {e}")
        test_results['core_components'] = False
    
    print()
    
    # Test Suite 3: Semantic Kernel Plugins
    print("📋 PHASE 3: Semantic Kernel Plugin Tests")
    print("-" * 50)
    try:
        test_results['plugins'] = run_plugin_tests()
    except Exception as e:
        print(f"❌ Plugin tests failed with exception: {e}")
        test_results['plugins'] = False
    
    print()
    
    # Test Suite 4: Integration Tests
    print("📋 PHASE 4: Integration Tests")
    print("-" * 50)
    try:
        test_results['integration'] = run_integration_tests()
    except Exception as e:
        print(f"❌ Integration tests failed with exception: {e}")
        test_results['integration'] = False
    
    print()
    
    # Final Results Summary
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_suites = len(test_results)
    passed_suites = sum(1 for result in test_results.values() if result)
    failed_suites = total_suites - passed_suites
    
    for suite_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{suite_name.replace('_', ' ').title():.<30} {status}")
    
    print("-" * 80)
    print(f"Test Suites: {passed_suites}/{total_suites} passed ({failed_suites} failed)")
    
    if failed_suites == 0:
        print("🎉 ALL TESTS PASSED! Document Eligibility Agent is ready for production.")
        success_rate = 100.0
    else:
        success_rate = (passed_suites / total_suites) * 100
        print(f"⚠️  Test Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("✨ Most tests passed - system is largely functional with minor issues.")
        elif success_rate >= 50:
            print("🔧 Moderate test failures - system needs attention before production.")
        else:
            print("🚨 Major test failures - system requires significant fixes.")
    
    print(f"Completed at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    return failed_suites == 0


def run_quick_validation():
    """Run a quick validation of the most critical components"""
    print("⚡ Document Eligibility Agent - Quick Validation")
    print("=" * 60)
    
    # Quick setup check
    print("🔧 Checking setup...", end=" ")
    try:
        from src.main import DocumentEligibilityAgent
        agent = DocumentEligibilityAgent(use_mock_services=True)
        print("✅ OK")
        setup_ok = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        setup_ok = False
    
    # Quick functionality check
    print("🧪 Testing core functionality...", end=" ")
    try:
        if setup_ok:
            import asyncio
            
            # Test email processing
            docs = asyncio.run(agent.process_email_batch(batch_size=1))
            assert len(docs) > 0
            
            # Test eligibility assessment
            from src.models.document_types import ApplicantRecord
            applicant = ApplicantRecord(
                applicant_id="QUICK_TEST",
                first_name="Quick",
                last_name="Test",
                email="quick@test.com",
                documents=docs
            )
            
            assessment = agent.assess_eligibility(applicant, "SNAP")
            assert assessment is not None
            
            print("✅ OK")
            functionality_ok = True
        else:
            print("⏭️ SKIPPED (setup failed)")
            functionality_ok = False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        functionality_ok = False
    
    # Results
    print("-" * 60)
    if setup_ok and functionality_ok:
        print("🎉 Quick validation PASSED - system is ready for use!")
        return True
    else:
        print("⚠️  Quick validation FAILED - run full tests for details")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking Dependencies")
    print("-" * 30)
    
    required_packages = [
        'semantic-kernel',
        'azure-ai-formrecognizer', 
        'azure-identity',
        'msgraph-sdk',
        'python-dotenv',
        'asyncio',
        'pytest'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle package name variations
            import_name = package.replace('-', '_').replace('semantic_kernel', 'semantic_kernel')
            if package == 'msgraph-sdk':
                import_name = 'msgraph'
            elif package == 'azure-ai-formrecognizer':
                import_name = 'azure.ai.formrecognizer'
            elif package == 'azure-identity':
                import_name = 'azure.identity'
            
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    print("-" * 30)
    if missing_packages:
        print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
        print("📥 Install with: pip install -r requirements.txt")
        return False
    else:
        print("🎉 All dependencies are installed!")
        return True


def main():
    """Main test runner entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'quick':
            success = run_quick_validation()
        elif command == 'deps':
            success = check_dependencies()
        elif command == 'setup':
            success = run_setup_tests()
        elif command == 'core':
            success = run_core_component_tests()
        elif command == 'plugins':
            success = run_plugin_tests()
        elif command == 'integration':
            success = run_integration_tests()
        elif command == 'all':
            success = run_all_tests()
        else:
            print("Usage: python run_all_tests.py [quick|deps|setup|core|plugins|integration|all]")
            print()
            print("Commands:")
            print("  quick       - Quick validation of core functionality")
            print("  deps        - Check dependencies installation")
            print("  setup       - Run setup and configuration tests")
            print("  core        - Run core component tests")
            print("  plugins     - Run Semantic Kernel plugin tests")
            print("  integration - Run integration tests")
            print("  all         - Run complete test suite (default)")
            return True
    else:
        # Default: run all tests
        success = run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)