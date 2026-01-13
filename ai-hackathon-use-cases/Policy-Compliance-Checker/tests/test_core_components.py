"""
Unit Tests for Policy Compliance Checker Core Components
Tests document parsing, compliance engine, and main application logic.
"""
import pytest
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import components to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.document_parser import DocumentParser, PolicyDocument
from src.core.compliance_engine import (
    ComplianceRulesEngine, ComplianceRule, ComplianceViolation, 
    ComplianceReport, ComplianceLevel
)


class TestDocumentParser:
    """Test the DocumentParser class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DocumentParser()
    
    def test_init(self):
        """Test DocumentParser initialization"""
        assert self.parser.supported_formats == ['.pdf', '.docx', '.txt', '.md']
    
    def test_parse_text_document(self):
        """Test parsing a text document"""
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Sample Policy\n\nThis is a test policy document.\n\n## Section 1\nContent here.")
            temp_path = f.name
        
        try:
            document = self.parser.parse_document(temp_path)
            
            assert isinstance(document, PolicyDocument)
            assert document.title == "Sample Policy"
            assert "test policy document" in document.content
            assert document.document_type == ".txt"
            assert len(document.sections) >= 1
            assert document.metadata['word_count'] > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_markdown_document(self):
        """Test parsing a markdown document"""
        content = """# Employee Code of Conduct

## Introduction
This document outlines our code of conduct.

## Professional Behavior
All employees must behave professionally.

## Confidentiality
Maintain confidentiality of company information.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            document = self.parser.parse_document(temp_path)
            
            assert document.title == "Employee Code of Conduct"
            assert len(document.sections) >= 3
            assert any("Professional Behavior" in section['title'] for section in document.sections)
            assert document.metadata['word_count'] > 10
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_document("nonexistent_file.txt")
    
    def test_parse_unsupported_format(self):
        """Test parsing an unsupported file format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                self.parser.parse_document(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_extract_title_from_content(self):
        """Test title extraction from document content"""
        content = "# Main Title\n\nSome content here"
        title = self.parser._extract_title(content, "test.txt")
        assert title == "Main Title"
    
    def test_extract_title_from_filename(self):
        """Test title extraction from filename when no title in content"""
        content = "Some content without a clear title"
        title = self.parser._extract_title(content, "/path/to/employee_handbook.txt")
        # Should extract title from filename when no clear title in content
        assert title == "Employee Handbook"
    
    def test_extract_sections(self):
        """Test section extraction"""
        content = """# Main Title

Introduction content here.

## Section One
Content for section one.

## Section Two  
Content for section two.
"""
        sections = self.parser._extract_sections(content)
        
        assert len(sections) >= 2
        section_titles = [s['title'] for s in sections]
        assert any("Section One" in title for title in section_titles)
        assert any("Section Two" in title for title in section_titles)
    
    def test_extract_metadata(self):
        """Test metadata extraction"""
        content = "This is a test document with multiple words and lines.\nSecond line here.\nDate mentioned: 2024-01-15"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            metadata = self.parser._extract_metadata(content, temp_path)
            
            assert metadata['word_count'] > 0
            assert metadata['character_count'] == len(content)
            assert metadata['line_count'] == 3
            assert metadata['file_extension'] == '.txt'
            assert 'dates_mentioned' in metadata
            
        finally:
            os.unlink(temp_path)


class TestComplianceEngine:
    """Test the ComplianceRulesEngine class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = ComplianceRulesEngine()
        
        # Create sample rules
        self.sample_rule_1 = ComplianceRule(
            id="rule_001",
            name="Required Privacy Section",
            description="Policy must include a privacy section",
            level=ComplianceLevel.HIGH,
            pattern="",
            rule_type="required_sections",
            required_sections=["Privacy", "Data Protection"],
            prohibited_terms=[],
            required_terms=[],
            metadata={"category": "legal"}
        )
        
        self.sample_rule_2 = ComplianceRule(
            id="rule_002", 
            name="No Discriminatory Language",
            description="Policy must not contain discriminatory language",
            level=ComplianceLevel.CRITICAL,
            pattern="",
            rule_type="prohibited_terms",
            required_sections=[],
            prohibited_terms=["discriminate", "exclude based on race"],
            required_terms=[],
            metadata={"category": "legal"}
        )
        
        self.sample_rule_3 = ComplianceRule(
            id="rule_003",
            name="Equal Opportunity Statement",
            description="Must include equal opportunity language",
            level=ComplianceLevel.MEDIUM,
            pattern="",
            rule_type="required_terms",
            required_sections=[],
            prohibited_terms=[],
            required_terms=["equal opportunity", "diversity"],
            metadata={"category": "legal"}
        )
    
    def test_init(self):
        """Test ComplianceRulesEngine initialization"""
        assert len(self.engine.rules) == 0
        assert "legal" in self.engine.rule_categories
    
    def test_add_rule(self):
        """Test adding a compliance rule"""
        self.engine.add_rule(self.sample_rule_1)
        assert len(self.engine.rules) == 1
        assert self.engine.rules[0].id == "rule_001"
    
    def test_load_rules_from_json(self):
        """Test loading rules from JSON file"""
        rules_data = {
            "rules": [
                {
                    "id": "test_rule",
                    "name": "Test Rule",
                    "description": "A test rule",
                    "level": "high",
                    "type": "required_sections",
                    "required_sections": ["Introduction"],
                    "prohibited_terms": [],
                    "required_terms": [],
                    "metadata": {"category": "test"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(rules_data, f)
            temp_path = f.name
        
        try:
            self.engine.load_rules_from_file(temp_path)
            assert len(self.engine.rules) == 1
            assert self.engine.rules[0].name == "Test Rule"
            assert self.engine.rules[0].level == ComplianceLevel.HIGH
        finally:
            os.unlink(temp_path)
    
    def test_load_rules_invalid_file(self):
        """Test loading rules from invalid file"""
        with pytest.raises(ValueError):
            self.engine.load_rules_from_file("nonexistent.json")
    
    def test_check_required_sections_pass(self):
        """Test required sections check - passing case"""
        # Create document with required sections
        document = Mock()
        document.sections = [
            {"title": "Introduction", "content": "intro"},
            {"title": "Privacy Policy", "content": "privacy"},
            {"title": "Data Protection", "content": "data"}
        ]
        document.content = "Sample policy content"
        document.title = "Test Policy"
        document.file_path = "test.txt"
        
        self.engine.add_rule(self.sample_rule_1)
        violations = self.engine._check_required_sections(document, self.sample_rule_1)
        
        # Should pass since document has "Privacy" and "Data Protection" sections
        assert len(violations) == 0
    
    def test_check_required_sections_fail(self):
        """Test required sections check - failing case"""
        # Create document without required sections
        document = Mock()
        document.sections = [
            {"title": "Introduction", "content": "intro"},
            {"title": "General Info", "content": "info"}
        ]
        document.content = "Sample policy content"
        document.title = "Test Policy"
        document.file_path = "test.txt"
        
        violations = self.engine._check_required_sections(document, self.sample_rule_1)
        
        # Should fail since missing Privacy and Data Protection sections
        assert len(violations) == 2
        assert all(v.level == ComplianceLevel.HIGH for v in violations)
    
    def test_check_prohibited_terms(self):
        """Test prohibited terms check"""
        document = Mock()
        document.content = "We do not discriminate against anyone based on race or gender."
        document.sections = []
        
        violations = self.engine._check_prohibited_terms(document, self.sample_rule_2)
        
        # Should find "discriminate" as prohibited term
        assert len(violations) == 1
        assert violations[0].level == ComplianceLevel.CRITICAL
        assert "discriminate" in violations[0].description.lower()
    
    def test_check_required_terms_pass(self):
        """Test required terms check - passing case""" 
        document = Mock()
        document.content = "We are an equal opportunity employer committed to diversity and inclusion."
        document.sections = []
        
        violations = self.engine._check_required_terms(document, self.sample_rule_3)
        
        # Should pass since both "equal opportunity" and "diversity" are present
        assert len(violations) == 0
    
    def test_check_required_terms_fail(self):
        """Test required terms check - failing case"""
        document = Mock()
        document.content = "We hire the best candidates for our company."
        document.sections = []
        
        violations = self.engine._check_required_terms(document, self.sample_rule_3)
        
        # Should fail since missing required terms
        assert len(violations) == 2  # Missing both terms
        assert all(v.level == ComplianceLevel.MEDIUM for v in violations)
    
    def test_check_compliance_full(self):
        """Test full compliance check"""
        # Create a mock document
        document = Mock()
        document.title = "Employee Handbook"
        document.file_path = "handbook.txt"
        document.content = "This handbook covers equal opportunity policies and our privacy section."
        document.sections = [
            {"title": "Privacy Policy", "content": "privacy details"},
            {"title": "Equal Opportunity", "content": "opportunity details"}
        ]
        
        # Add rules
        self.engine.add_rule(self.sample_rule_1)  # Required sections
        self.engine.add_rule(self.sample_rule_3)  # Required terms
        
        report = self.engine.check_compliance(document)
        
        assert isinstance(report, ComplianceReport)
        assert report.document_title == "Employee Handbook"
        assert report.total_rules_checked == 2
        assert 0 <= report.compliance_score <= 100
        assert isinstance(report.violations, list)
        assert isinstance(report.summary, dict)
    
    def test_get_violation_weight(self):
        """Test violation weight calculation"""
        assert self.engine._get_violation_weight(ComplianceLevel.CRITICAL) == 10.0
        assert self.engine._get_violation_weight(ComplianceLevel.HIGH) == 5.0
        assert self.engine._get_violation_weight(ComplianceLevel.MEDIUM) == 3.0
        assert self.engine._get_violation_weight(ComplianceLevel.LOW) == 1.0
        assert self.engine._get_violation_weight(ComplianceLevel.INFO) == 0.1
    
    def test_get_rules_by_category(self):
        """Test filtering rules by category"""
        self.engine.add_rule(self.sample_rule_1)  # category: legal
        self.engine.add_rule(self.sample_rule_2)  # category: legal
        
        legal_rules = self.engine.get_rules_by_category("legal")
        assert len(legal_rules) == 2
        
        security_rules = self.engine.get_rules_by_category("security")
        assert len(security_rules) == 0
    
    def test_get_rule_by_id(self):
        """Test getting rule by ID"""
        self.engine.add_rule(self.sample_rule_1)
        
        rule = self.engine.get_rule_by_id("rule_001")
        assert rule is not None
        assert rule.name == "Required Privacy Section"
        
        missing_rule = self.engine.get_rule_by_id("nonexistent")
        assert missing_rule is None


class TestPolicyDocument:
    """Test the PolicyDocument dataclass"""
    
    def test_policy_document_creation(self):
        """Test creating a PolicyDocument"""
        document = PolicyDocument(
            title="Test Policy",
            content="This is test content",
            document_type=".txt",
            file_path="/test/path.txt",
            metadata={"word_count": 4},
            sections=[{"title": "Section 1", "content": "content"}],
            created_at=datetime.now()
        )
        
        assert document.title == "Test Policy"
        assert document.content == "This is test content"
        assert document.document_type == ".txt"
        assert len(document.sections) == 1


class TestComplianceDataClasses:
    """Test compliance-related data classes"""
    
    def test_compliance_violation(self):
        """Test ComplianceViolation creation"""
        violation = ComplianceViolation(
            rule_id="test_rule",
            rule_name="Test Rule",
            level=ComplianceLevel.HIGH,
            description="Test violation",
            location="Section 1",
            context="Test context",
            suggestion="Fix this issue"
        )
        
        assert violation.rule_id == "test_rule"
        assert violation.level == ComplianceLevel.HIGH
        assert violation.description == "Test violation"
    
    def test_compliance_report(self):
        """Test ComplianceReport creation"""
        violations = [
            ComplianceViolation(
                rule_id="rule1", rule_name="Rule 1", level=ComplianceLevel.HIGH,
                description="Issue 1", location="Loc 1", context="Context 1", suggestion="Fix 1"
            )
        ]
        
        report = ComplianceReport(
            document_title="Test Doc",
            document_path="/test/doc.txt",
            total_rules_checked=5,
            violations=violations,
            compliance_score=85.0,
            checked_at=datetime.now(),
            summary={"high": 1, "medium": 0, "low": 0, "critical": 0, "info": 0}
        )
        
        assert report.document_title == "Test Doc"
        assert report.compliance_score == 85.0
        assert len(report.violations) == 1
        assert report.summary["high"] == 1


def run_unit_tests():
    """Run all unit tests manually"""
    print("🧪 Running Policy Compliance Checker Unit Tests")
    print("=" * 60)
    
    test_classes = [
        TestDocumentParser,
        TestComplianceEngine, 
        TestPolicyDocument,
        TestComplianceDataClasses
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        print("-" * 40)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            
            try:
                # Create instance and run setup if exists
                instance = test_class()
                if hasattr(instance, 'setup_method'):
                    instance.setup_method()
                
                # Run the test
                test_method = getattr(instance, method_name)
                test_method()
                
                print(f"  ✅ {method_name}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ❌ {method_name} - FAILED: {str(e)}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 UNIT TEST SUMMARY")
    print("=" * 60)
    print(f"🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for class_name, method_name, error in failed_tests:
            print(f"   • {class_name}.{method_name}")
            print(f"     Error: {error}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL UNIT TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {len(failed_tests)} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_unit_tests()
    
    print("\n💡 To run with pytest framework:")
    print("   pytest tests/test_core_components.py -v")
    
    exit(0 if success else 1)