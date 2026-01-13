"""
Emergency Response Agent - Comprehensive Test Runner
Runs all tests with detailed reporting and coverage.
"""
import pytest
import sys
import os
from pathlib import Path
import subprocess
import json


def run_all_tests():
    """Run all tests with comprehensive reporting."""
    
    print("🚨 Emergency Response Agent - Test Suite")
    print("=" * 60)
    
    # Add src to Python path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Test categories with their descriptions
    test_categories = {
        "test_setup.py": "Setup and Configuration Tests",
        "test_models.py": "Data Model Tests", 
        "test_weather_service.py": "Weather Service Tests",
        "test_emergency_coordinator.py": "Emergency Coordinator Tests",
        "test_integration.py": "Integration Tests"
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    print("📋 Test Categories:")
    for test_file, description in test_categories.items():
        print(f"  • {description} ({test_file})")
    print()
    
    # Run tests with detailed output
    test_results = []
    
    for test_file, description in test_categories.items():
        print(f"🧪 Running {description}...")
        
        # Run individual test file
        result = pytest.main([
            f"tests/{test_file}",
            "-v",
            "--tb=short",
            "--no-header"
        ])
        
        if result == 0:
            status = "✅ PASSED"
            passed_tests += 1
        else:
            status = "❌ FAILED" 
            failed_tests += 1
        
        test_results.append({
            "category": description,
            "file": test_file,
            "status": status,
            "exit_code": result
        })
        
        total_tests += 1
        print(f"   {status}")
        print()
    
    # Summary report
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for result in test_results:
        print(f"{result['status']} {result['category']}")
    
    print()
    print(f"📈 Overall Results:")
    print(f"  Total Test Categories: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Emergency Response Agent is ready!")
        return True
    else:
        print(f"\n⚠️  {failed_tests} test categories failed. Review output above.")
        return False


def run_individual_test_with_details(test_file):
    """Run individual test file with detailed output."""
    print(f"🔍 Detailed Test Run: {test_file}")
    print("-" * 50)
    
    # Run with maximum verbosity
    result = pytest.main([
        f"tests/{test_file}",
        "-v",
        "--tb=long",
        "--capture=no"
    ])
    
    return result == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        success = run_individual_test_with_details(test_file)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = run_all_tests()
        sys.exit(0 if success else 1)