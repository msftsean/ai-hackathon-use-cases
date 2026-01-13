"""
Integration Tests for Policy Compliance Checker
Tests the complete workflow and integration between components.
"""
import pytest
import tempfile
import os
import json
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import main application
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import PolicyComplianceChecker
from src.core.document_parser import PolicyDocument
from src.core.compliance_engine import ComplianceLevel


class TestPolicyComplianceCheckerIntegration:
    """Integration tests for the main PolicyComplianceChecker class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Initialize without AI credentials for basic testing
        self.checker = PolicyComplianceChecker()
    
    def test_initialization_without_ai(self):
        """Test initializing checker without AI credentials"""
        assert self.checker.ai_analysis_enabled is False
        assert self.checker.policy_analysis_plugin is None
        assert self.checker.policy_improvement_plugin is None
    
    def test_initialization_with_ai_credentials(self):
        """Test initializing checker with AI credentials"""
        checker = PolicyComplianceChecker(
            azure_openai_deployment="test-deployment",
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key"
        )
        
        assert checker.ai_analysis_enabled is True
        assert checker.policy_analysis_plugin is not None
        assert checker.policy_improvement_plugin is not None
    
    @pytest.mark.asyncio
    async def test_initialize_method(self):
        """Test the initialize method"""
        # Should not raise any exceptions
        await self.checker.initialize()
        
        # Verify document parser and compliance engine are ready
        assert self.checker.document_parser is not None
        assert self.checker.compliance_engine is not None
    
    def test_load_compliance_rules(self):
        """Test loading compliance rules from file"""
        # Create sample rules JSON
        rules_data = {
            "rules": [
                {
                    "id": "test_rule_1",
                    "name": "Privacy Section Required",
                    "description": "Document must have a privacy section",
                    "level": "high",
                    "type": "required_sections",
                    "required_sections": ["Privacy"],
                    "prohibited_terms": [],
                    "required_terms": [],
                    "metadata": {"category": "legal"}
                },
                {
                    "id": "test_rule_2", 
                    "name": "No Offensive Language",
                    "description": "Document must not contain offensive terms",
                    "level": "critical",
                    "type": "prohibited_terms",
                    "required_sections": [],
                    "prohibited_terms": ["offensive", "inappropriate"],
                    "required_terms": [],
                    "metadata": {"category": "content"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            temp_path = f.name
        
        try:
            self.checker.load_compliance_rules(temp_path)
            assert len(self.checker.compliance_engine.rules) == 2
            
            # Test rule details
            rules = self.checker.compliance_engine.rules
            assert rules[0].name == "Privacy Section Required"
            assert rules[1].level == ComplianceLevel.CRITICAL
            
        finally:
            os.unlink(temp_path)
    
    def test_load_compliance_rules_file_not_found(self):
        """Test loading rules from non-existent file"""
        with pytest.raises(FileNotFoundError):
            self.checker.load_compliance_rules("nonexistent_rules.json")
    
    def test_parse_document(self):
        """Test parsing a document"""
        content = """# Employee Code of Conduct

## Introduction
This document outlines expected behavior.

## Privacy Policy
We protect employee privacy and personal data.

## Professional Standards
All employees must maintain professional standards.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            document = self.checker.parse_document(temp_path)
            
            assert isinstance(document, PolicyDocument)
            assert document.title == "Employee Code of Conduct"
            assert len(document.sections) >= 3
            assert "Privacy Policy" in [s['title'] for s in document.sections]
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_document_file_not_found(self):
        """Test parsing non-existent document"""
        with pytest.raises(FileNotFoundError):
            self.checker.parse_document("nonexistent_document.txt")
    
    def test_check_compliance_complete_workflow(self):
        """Test complete compliance checking workflow"""
        # Create document
        content = """# Privacy Policy

## Introduction
This policy explains how we handle data.

## Privacy Policy
We protect all personal information and maintain strict confidentiality.

## Data Collection  
We collect necessary information only for business purposes.

## Equal Opportunity
We provide equal opportunities to all employees and maintain diversity.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            doc_path = f.name
        
        # Create rules
        rules_data = {
            "rules": [
                {
                    "id": "privacy_required",
                    "name": "Privacy Section Required",
                    "description": "Must have privacy section",
                    "level": "high",
                    "type": "required_sections",
                    "required_sections": ["Privacy", "Data Collection"],
                    "prohibited_terms": [],
                    "required_terms": [],
                    "metadata": {"category": "legal"}
                },
                {
                    "id": "equal_opportunity_terms",
                    "name": "Equal Opportunity Language",
                    "description": "Must include equal opportunity terms",
                    "level": "medium",
                    "type": "required_terms",
                    "required_sections": [],
                    "prohibited_terms": [],
                    "required_terms": ["equal opportunity"],
                    "metadata": {"category": "legal"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            rules_path = f.name
        
        try:
            # Complete workflow
            self.checker.load_compliance_rules(rules_path)
            document = self.checker.parse_document(doc_path)
            report = self.checker.check_compliance(document)
            
            # Verify report
            assert report.document_title == "Privacy Policy"
            assert report.total_rules_checked == 2
            assert 0 <= report.compliance_score <= 100
            assert isinstance(report.violations, list)
            
            # Should pass both rules (has privacy sections and equal opportunity terms)
            # Privacy Policy document should match the Privacy requirement
            # Equal opportunity terms should be found
            print(f"Violations found: {len(report.violations)}")
            print(f"Compliance score: {report.compliance_score}")
            for v in report.violations:
                print(f"  - {v.description}")
            
            # Should have good compliance score since document has privacy section and equal opportunity terms
            assert report.compliance_score >= 75  # Document should pass both main requirements
            
        finally:
            os.unlink(doc_path)
            os.unlink(rules_path)
    
    def test_check_compliance_with_violations(self):
        """Test compliance checking with violations"""
        # Create document with violations
        content = """# Basic Policy

Just some basic content without required sections.
Contains inappropriate language that should be flagged.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            doc_path = f.name
        
        # Create strict rules
        rules_data = {
            "rules": [
                {
                    "id": "required_sections",
                    "name": "Required Sections",
                    "description": "Must have required sections",
                    "level": "high",
                    "type": "required_sections",
                    "required_sections": ["Privacy Policy", "Code of Conduct"],
                    "prohibited_terms": [],
                    "required_terms": [],
                    "metadata": {"category": "structure"}
                },
                {
                    "id": "no_inappropriate",
                    "name": "No Inappropriate Language", 
                    "description": "Must not contain inappropriate terms",
                    "level": "critical",
                    "type": "prohibited_terms",
                    "required_sections": [],
                    "prohibited_terms": ["inappropriate"],
                    "required_terms": [],
                    "metadata": {"category": "content"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            rules_path = f.name
        
        try:
            self.checker.load_compliance_rules(rules_path)
            document = self.checker.parse_document(doc_path)
            report = self.checker.check_compliance(document)
            
            # Should have violations
            assert len(report.violations) > 0
            assert report.compliance_score < 100
            
            # Check violation details
            violation_descriptions = [v.description for v in report.violations]
            assert any("Privacy Policy" in desc for desc in violation_descriptions)
            assert any("inappropriate" in desc.lower() for desc in violation_descriptions)
            
        finally:
            os.unlink(doc_path)
            os.unlink(rules_path)
    
    def test_check_compliance_no_rules_loaded(self):
        """Test compliance checking without loading rules first"""
        content = "# Test Document\n\nSome content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            doc_path = f.name
        
        try:
            document = self.checker.parse_document(doc_path)
            
            with pytest.raises(ValueError, match="No compliance rules loaded"):
                self.checker.check_compliance(document)
                
        finally:
            os.unlink(doc_path)
    
    def test_generate_report(self):
        """Test report generation"""
        # Create mock document and compliance report
        document = Mock()
        document.title = "Test Policy"
        document.file_path = "/test/policy.md"
        document.metadata = {"word_count": 150}
        document.sections = [{"title": "Section 1", "content": "content"}]
        
        compliance_report = Mock()
        compliance_report.compliance_score = 85.5
        compliance_report.total_rules_checked = 3
        compliance_report.checked_at = datetime.now()
        compliance_report.summary = {"critical": 0, "high": 1, "medium": 0, "low": 0, "info": 0}
        compliance_report.violations = []
        
        # Generate report
        report_json = self.checker.generate_report(document, compliance_report)
        
        # Parse and verify
        report_data = json.loads(report_json)
        
        assert report_data["document_info"]["title"] == "Test Policy"
        assert report_data["compliance_results"]["score"] == 85.5
        assert report_data["compliance_results"]["total_rules_checked"] == 3
    
    def test_generate_report_with_output_file(self):
        """Test report generation with file output"""
        document = Mock()
        document.title = "Test Policy"
        document.file_path = "/test/policy.md"
        document.metadata = {"word_count": 150}
        document.sections = []
        
        compliance_report = Mock()
        compliance_report.compliance_score = 90.0
        compliance_report.total_rules_checked = 2
        compliance_report.checked_at = datetime.now()
        compliance_report.summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        compliance_report.violations = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            report_json = self.checker.generate_report(
                document, compliance_report, output_path=output_path
            )
            
            # Verify file was created
            assert os.path.exists(output_path)
            
            # Verify file content
            with open(output_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["document_info"]["title"] == "Test Policy"
            assert saved_data["compliance_results"]["score"] == 90.0
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_list_available_rules(self):
        """Test listing available rules"""
        # Load some rules first
        rules_data = {
            "rules": [
                {
                    "id": "rule1",
                    "name": "Rule One",
                    "description": "First rule",
                    "level": "high",
                    "type": "required_sections",
                    "required_sections": ["Section1"],
                    "prohibited_terms": [],
                    "required_terms": [],
                    "metadata": {"category": "legal"}
                },
                {
                    "id": "rule2",
                    "name": "Rule Two", 
                    "description": "Second rule",
                    "level": "medium",
                    "type": "prohibited_terms",
                    "required_sections": [],
                    "prohibited_terms": ["badword"],
                    "required_terms": [],
                    "metadata": {"category": "content"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            temp_path = f.name
        
        try:
            self.checker.load_compliance_rules(temp_path)
            rules_info = self.checker.list_available_rules()
            
            assert len(rules_info) == 2
            assert rules_info[0]["id"] == "rule1"
            assert rules_info[0]["name"] == "Rule One"
            assert rules_info[0]["level"] == "high"
            assert rules_info[0]["category"] == "legal"
            
            assert rules_info[1]["type"] == "prohibited_terms"
            assert rules_info[1]["category"] == "content"
            
        finally:
            os.unlink(temp_path)
    
    def test_get_rule_categories(self):
        """Test getting rules organized by category"""
        # Load rules with different categories
        rules_data = {
            "rules": [
                {
                    "id": "legal1",
                    "name": "Legal Rule 1",
                    "description": "Legal rule",
                    "level": "high",
                    "type": "required_sections",
                    "required_sections": [],
                    "prohibited_terms": [],
                    "required_terms": [],
                    "metadata": {"category": "legal"}
                },
                {
                    "id": "legal2",
                    "name": "Legal Rule 2",
                    "description": "Another legal rule",
                    "level": "medium",
                    "type": "required_terms",
                    "required_sections": [],
                    "prohibited_terms": [],
                    "required_terms": ["term"],
                    "metadata": {"category": "legal"}
                },
                {
                    "id": "security1",
                    "name": "Security Rule",
                    "description": "Security rule",
                    "level": "critical",
                    "type": "prohibited_terms",
                    "required_sections": [],
                    "prohibited_terms": ["password"],
                    "required_terms": [],
                    "metadata": {"category": "security"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            temp_path = f.name
        
        try:
            self.checker.load_compliance_rules(temp_path)
            categories = self.checker.get_rule_categories()
            
            assert "legal" in categories
            assert "security" in categories
            assert len(categories["legal"]) == 2
            assert len(categories["security"]) == 1
            assert "legal1" in categories["legal"]
            assert "legal2" in categories["legal"]
            assert "security1" in categories["security"]
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_ai_features_disabled_without_credentials(self):
        """Test that AI features are properly disabled without credentials"""
        with pytest.raises(ValueError, match="AI analysis not available"):
            await self.checker.ai_analyze_document(Mock())
        
        with pytest.raises(ValueError, match="AI analysis not available"):
            await self.checker.ai_suggest_improvements(Mock())
        
        with pytest.raises(ValueError, match="AI analysis not available"):
            await self.checker.ai_compare_documents(Mock(), Mock())


def run_integration_tests():
    """Run all integration tests manually"""
    print("🔗 Running Policy Compliance Checker Integration Tests")
    print("=" * 60)
    
    test_class = TestPolicyComplianceCheckerIntegration
    
    # Get all test methods (excluding async ones for manual run)
    test_methods = [
        method for method in dir(test_class) 
        if method.startswith('test_') and 'ai_' not in method
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    print(f"📋 Testing {test_class.__name__}")
    print("-" * 40)
    
    for method_name in test_methods:
        total_tests += 1
        
        try:
            # Create instance and run setup
            instance = test_class()
            instance.setup_method()
            
            # Run the test
            test_method = getattr(instance, method_name)
            test_method()
            
            print(f"  ✅ {method_name}")
            passed_tests += 1
            
        except Exception as e:
            print(f"  ❌ {method_name} - FAILED: {str(e)}")
            failed_tests.append((method_name, str(e)))
    
    # Test AI feature error handling
    print("\n📋 Testing AI Feature Error Handling")
    print("-" * 40)
    
    try:
        instance = test_class()
        instance.setup_method()
        
        # Test AI features when disabled
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(instance.test_ai_features_disabled_without_credentials())
            print("  ✅ test_ai_features_disabled_without_credentials")
            passed_tests += 1
        except Exception as e:
            print(f"  ❌ test_ai_features_disabled_without_credentials - FAILED: {str(e)}")
            failed_tests.append(("test_ai_features_disabled_without_credentials", str(e)))
        finally:
            loop.close()
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ AI test setup failed: {str(e)}")
        failed_tests.append(("AI test setup", str(e)))
        total_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for method_name, error in failed_tests:
            print(f"   • {method_name}")
            print(f"     Error: {error}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {len(failed_tests)} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    
    print("\n💡 To run with pytest framework:")
    print("   pytest tests/test_integration.py -v")
    print("   pytest tests/test_integration.py::TestPolicyComplianceCheckerIntegration::test_check_compliance_complete_workflow -v")
    
    exit(0 if success else 1)