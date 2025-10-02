"""
Plugin-specific tests for Document Eligibility Agent Semantic Kernel plugins
"""
import pytest
from unittest.mock import patch, MagicMock

from src.plugins.document_processing_plugins import (
    DocumentClassificationPlugin,
    DataExtractionPlugin,
    EligibilityCalculationPlugin
)
from src.models.document_types import DocumentType, EligibilityCriteria


class TestDocumentClassificationPlugin:
    """Test DocumentClassificationPlugin functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.plugin = DocumentClassificationPlugin()
    
    def test_income_document_classification(self):
        """Test classification of income-related documents"""
        test_cases = [
            ("pay_stub_march_2024.pdf", "gross pay $3500 employee john doe", DocumentType.INCOME_VERIFICATION.value),
            ("salary_statement.pdf", "monthly salary total compensation", DocumentType.INCOME_VERIFICATION.value),
            ("w2_form_2023.pdf", "wages tax withholdings", DocumentType.INCOME_VERIFICATION.value),
            ("1099_freelance.pdf", "1099 independent contractor income", DocumentType.INCOME_VERIFICATION.value),
            ("employment_verification.pdf", "income employment verification letter", DocumentType.INCOME_VERIFICATION.value)
        ]
        
        for filename, text, expected in test_cases:
            result = self.plugin.classify_document_type(filename, text)
            assert result == expected, f"Failed for {filename}: expected {expected}, got {result}"
    
    def test_medical_document_classification(self):
        """Test classification of medical documents"""
        test_cases = [
            ("insurance_card.jpg", "patient name policy number blue cross", DocumentType.MEDICAL_RECORD.value),
            ("medical_record.pdf", "doctor visit prescription treatment", DocumentType.MEDICAL_RECORD.value),
            ("health_insurance.pdf", "health insurance coverage patient", DocumentType.MEDICAL_RECORD.value),
            ("prescription_receipt.pdf", "prescription medication patient pharmacy", DocumentType.MEDICAL_RECORD.value)
        ]
        
        for filename, text, expected in test_cases:
            result = self.plugin.classify_document_type(filename, text)
            assert result == expected, f"Failed for {filename}: expected {expected}, got {result}"
    
    def test_utility_document_classification(self):
        """Test classification of utility bills"""
        test_cases = [
            ("electric_bill_march.pdf", "utility electric bill amount due", DocumentType.UTILITY_BILL.value),
            ("gas_bill.pdf", "gas utility service billing statement", DocumentType.UTILITY_BILL.value),
            ("water_bill.pdf", "water utility account billing", DocumentType.UTILITY_BILL.value),
            ("energy_bill.pdf", "energy power utility billing", DocumentType.UTILITY_BILL.value)
        ]
        
        for filename, text, expected in test_cases:
            result = self.plugin.classify_document_type(filename, text)
            assert result == expected, f"Failed for {filename}: expected {expected}, got {result}"
    
    def test_identity_document_classification(self):
        """Test classification of identity documents"""
        test_cases = [
            ("drivers_license.jpg", "drivers license state issued", DocumentType.IDENTITY_DOCUMENT.value),
            ("passport.pdf", "passport travel document citizenship", DocumentType.IDENTITY_DOCUMENT.value),
            ("ssn_card.jpg", "social security number card", DocumentType.IDENTITY_DOCUMENT.value),
            ("birth_certificate.pdf", "birth certificate official record", DocumentType.IDENTITY_DOCUMENT.value)
        ]
        
        for filename, text, expected in test_cases:
            result = self.plugin.classify_document_type(filename, text)
            assert result == expected, f"Failed for {filename}: expected {expected}, got {result}"
    
    def test_unknown_document_classification(self):
        """Test classification of unknown documents"""
        test_cases = [
            ("random_file.txt", "some random text content", DocumentType.UNKNOWN.value),
            ("meeting_notes.docx", "meeting agenda discussion points", DocumentType.UNKNOWN.value),
            ("photo.jpg", "family vacation picture", DocumentType.UNKNOWN.value)
        ]
        
        for filename, text, expected in test_cases:
            result = self.plugin.classify_document_type(filename, text)
            assert result == expected, f"Failed for {filename}: expected {expected}, got {result}"
    
    def test_classification_confidence_validation(self):
        """Test classification confidence scoring"""
        # High confidence case - income document with clear indicators
        extracted_fields = {
            'income_amount': 3500.0,
            'pay_date': '2024-03-15',
            'employee_name': 'John Doe',
            'employer': 'Acme Corp'
        }
        
        confidence = self.plugin.validate_classification(
            DocumentType.INCOME_VERIFICATION.value,
            extracted_fields
        )
        assert confidence > 0.8
        
        # Medium confidence case - some relevant fields
        partial_fields = {
            'income_amount': 3500.0,
            'unknown_field': 'some value'
        }
        
        confidence = self.plugin.validate_classification(
            DocumentType.INCOME_VERIFICATION.value,
            partial_fields
        )
        assert 0.5 < confidence <= 0.8
        
        # Low confidence case - no relevant fields
        irrelevant_fields = {
            'random_field': 'random value',
            'another_field': 'another value'
        }
        
        confidence = self.plugin.validate_classification(
            DocumentType.INCOME_VERIFICATION.value,
            irrelevant_fields
        )
        assert confidence <= 0.5


class TestDataExtractionPlugin:
    """Test DataExtractionPlugin functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.plugin = DataExtractionPlugin()
    
    def test_income_information_extraction(self):
        """Test extraction of income-specific information"""
        sample_income_text = """
        PAY STATEMENT
        Employee: John Smith
        Employee ID: EMP123456
        Pay Period: 03/01/2024 - 03/31/2024
        
        EARNINGS:
        Regular Hours: 160.00 @ $25.00/hr = $4,000.00
        Overtime Hours: 10.00 @ $37.50/hr = $375.00
        Gross Pay: $4,375.00
        
        DEDUCTIONS:
        Federal Tax: $875.00
        State Tax: $262.50
        Social Security: $271.25
        Medicare: $63.44
        
        Net Pay: $2,902.81
        
        Employer: Tech Solutions Inc.
        """
        
        result = self.plugin.extract_key_information(
            DocumentType.INCOME_VERIFICATION.value,
            sample_income_text
        )
        
        # Should extract income amount
        assert any('4375' in str(value) or '4,375' in str(value) for value in result.values())
        
        # Should extract employer information
        assert any('tech solutions' in str(value).lower() for value in result.values())
    
    def test_medical_information_extraction(self):
        """Test extraction of medical record information"""
        sample_medical_text = """
        MEDICAL RECORD
        Patient Name: Jane Doe
        Date of Birth: 01/15/1985
        Patient ID: PAT789012
        
        Visit Date: March 10, 2024
        Provider: Dr. Sarah Johnson, MD
        
        Insurance Information:
        Insurance Provider: Blue Cross Blue Shield
        Policy Number: BC123456789
        Group Number: GRP456
        
        Diagnosis: Annual Physical Exam
        Treatment: Routine checkup, blood work ordered
        """
        
        result = self.plugin.extract_key_information(
            DocumentType.MEDICAL_RECORD.value,
            sample_medical_text
        )
        
        # Should extract patient information
        assert any('jane doe' in str(value).lower() for value in result.values())
        
        # Should extract insurance information
        assert any('blue cross' in str(value).lower() for value in result.values())
    
    def test_utility_information_extraction(self):
        """Test extraction of utility bill information"""
        sample_utility_text = """
        ELECTRIC UTILITY BILL
        Account Number: ELEC567890
        Service Period: February 1-28, 2024
        
        Service Address:
        123 Main Street
        Anytown, ST 12345
        
        Billing Summary:
        Previous Balance: $0.00
        Current Charges: $145.67
        Amount Due: $145.67
        Due Date: March 25, 2024
        
        Usage: 1,250 kWh
        Rate: $0.12 per kWh
        """
        
        result = self.plugin.extract_key_information(
            DocumentType.UTILITY_BILL.value,
            sample_utility_text
        )
        
        # Should extract service address
        assert any('123 main street' in str(value).lower() for value in result.values())
        
        # Should extract amount due
        assert any('145.67' in str(value) for value in result.values())
    
    def test_extraction_quality_validation(self):
        """Test data extraction quality validation"""
        # High quality extraction
        high_quality_data = {
            'income_amount': '3500.00',
            'employee_name': 'John Doe',
            'employer': 'Acme Corporation',
            'pay_date': '2024-03-15',
            'pay_period': 'Monthly'
        }
        
        result = self.plugin.validate_extraction_quality(high_quality_data)
        assert result['quality_score'] > 0.8
        assert result['completeness'] == 1.0
        assert len(result['issues']) == 0
        
        # Medium quality extraction
        medium_quality_data = {
            'income_amount': '3500.00',
            'employee_name': 'John Doe',
            'unknown_field': '',  # Empty value
            'partial_data': None  # None value
        }
        
        result = self.plugin.validate_extraction_quality(medium_quality_data)
        assert 0.3 < result['quality_score'] < 0.8
        assert result['completeness'] < 1.0
        assert len(result['issues']) > 0
        
        # Poor quality extraction
        poor_quality_data = {
            'field1': '',
            'field2': None,
            'field3': '   ',  # Whitespace only
        }
        
        result = self.plugin.validate_extraction_quality(poor_quality_data)
        assert result['quality_score'] < 0.3
        assert result['completeness'] == 0.0
        assert len(result['issues']) == 3
    
    def test_empty_extraction_handling(self):
        """Test handling of empty extraction results"""
        empty_data = {}
        
        result = self.plugin.validate_extraction_quality(empty_data)
        assert result['quality_score'] == 0.0
        assert result['completeness'] == 0.0
        assert 'No data extracted' in result['issues']


class TestEligibilityCalculationPlugin:
    """Test EligibilityCalculationPlugin functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.plugin = EligibilityCalculationPlugin()
    
    def test_snap_eligibility_calculation(self):
        """Test SNAP program eligibility calculation"""
        # Test eligible case
        eligible_result = self.plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=1500.0,
            household_size=2,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.UTILITY_BILL.value
            ]
        )
        
        assert eligible_result['eligible'] is True
        assert eligible_result['confidence'] > 0.8
        assert len(eligible_result['missing_documents']) == 0
        assert eligible_result['income_assessment']['income_eligible'] is True
        
        # Test ineligible case - high income
        ineligible_result = self.plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=5000.0,
            household_size=1,
            available_documents=[DocumentType.INCOME_VERIFICATION.value]
        )
        
        assert ineligible_result['eligible'] is False
        assert 'income' in ineligible_result['reason'].lower()
        assert ineligible_result['income_assessment']['income_eligible'] is False
    
    def test_medicaid_eligibility_calculation(self):
        """Test Medicaid program eligibility calculation"""
        # Test with lower income threshold
        result = self.plugin.calculate_eligibility(
            program_name='Medicaid',
            monthly_income=1200.0,
            household_size=1,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.MEDICAL_RECORD.value
            ]
        )
        
        assert result['eligible'] is True
        assert len(result['missing_documents']) == 0
        
        # Test with income above Medicaid threshold but below SNAP threshold
        result = self.plugin.calculate_eligibility(
            program_name='Medicaid',
            monthly_income=1800.0,
            household_size=1,
            available_documents=[DocumentType.INCOME_VERIFICATION.value]
        )
        
        assert result['eligible'] is False
    
    def test_housing_assistance_eligibility(self):
        """Test Housing Assistance program eligibility"""
        result = self.plugin.calculate_eligibility(
            program_name='Housing_Assistance',
            monthly_income=2500.0,
            household_size=3,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.HOUSING_DOCUMENT.value,
                DocumentType.UTILITY_BILL.value
            ]
        )
        
        assert result['eligible'] is True
        assert len(result['missing_documents']) == 0
        
        # Verify higher income threshold for housing assistance
        assert result['income_assessment']['threshold'] > 3000.0  # Should be adjusted for household size
    
    def test_missing_documents_detection(self):
        """Test detection of missing required documents"""
        result = self.plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=1500.0,
            household_size=1,
            available_documents=[DocumentType.INCOME_VERIFICATION.value]  # Missing identity and utility
        )
        
        assert result['eligible'] is False
        assert len(result['missing_documents']) == 2
        assert DocumentType.IDENTITY_DOCUMENT.value in result['missing_documents']
        assert DocumentType.UTILITY_BILL.value in result['missing_documents']
        assert 'missing' in result['reason'].lower()
    
    def test_household_size_adjustment(self):
        """Test income threshold adjustment based on household size"""
        # Single person household
        single_result = self.plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=2000.0,
            household_size=1,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.UTILITY_BILL.value
            ]
        )
        
        # Larger household
        family_result = self.plugin.calculate_eligibility(
            program_name='SNAP',
            monthly_income=2000.0,
            household_size=4,
            available_documents=[
                DocumentType.INCOME_VERIFICATION.value,
                DocumentType.IDENTITY_DOCUMENT.value,
                DocumentType.UTILITY_BILL.value
            ]
        )
        
        # Larger household should have higher threshold, potentially making them eligible
        single_threshold = single_result['income_assessment']['threshold']
        family_threshold = family_result['income_assessment']['threshold']
        
        assert family_threshold > single_threshold
    
    def test_unknown_program_handling(self):
        """Test handling of unknown program names"""
        result = self.plugin.calculate_eligibility(
            program_name='UNKNOWN_PROGRAM',
            monthly_income=1500.0,
            household_size=1,
            available_documents=[]
        )
        
        assert result['eligible'] is False
        assert 'unknown program' in result['reason'].lower()
        assert result['confidence'] == 0.0
    
    def test_recommendation_generation(self):
        """Test generation of eligibility recommendations"""
        # Test recommendations for eligible applicant
        eligible_assessment = {
            'eligible': True,
            'reason': 'Meets all requirements',
            'missing_documents': []
        }
        
        recommendations = self.plugin.generate_recommendations(
            eligible_assessment,
            {'applicant_id': 'TEST_001', 'monthly_income': 1500.0}
        )
        
        assert len(recommendations) > 0
        assert any('✅' in rec for rec in recommendations)  # Should have positive indicators
        assert any('eligible' in rec.lower() for rec in recommendations)
        
        # Test recommendations for ineligible applicant (high income)
        ineligible_assessment = {
            'eligible': False,
            'reason': 'Income exceeds program limits',
            'missing_documents': []
        }
        
        recommendations = self.plugin.generate_recommendations(
            ineligible_assessment,
            {'applicant_id': 'TEST_002', 'monthly_income': 5000.0}
        )
        
        assert any('❌' in rec for rec in recommendations)  # Should have negative indicators
        assert any('income' in rec.lower() for rec in recommendations)
        
        # Test recommendations for applicant with missing documents
        missing_docs_assessment = {
            'eligible': False,
            'reason': 'Missing required documents',
            'missing_documents': ['identity_document', 'utility_bill']
        }
        
        recommendations = self.plugin.generate_recommendations(
            missing_docs_assessment,
            {'applicant_id': 'TEST_003'}
        )
        
        assert any('📄' in rec for rec in recommendations)  # Should mention documents
        assert any('identity' in rec.lower() for rec in recommendations)
    
    def test_program_criteria_configuration(self):
        """Test that program criteria are properly configured"""
        # Verify all expected programs are configured
        expected_programs = ['SNAP', 'Medicaid', 'Housing_Assistance']
        for program in expected_programs:
            assert program in self.plugin.program_criteria
            
            criteria = self.plugin.program_criteria[program]
            assert isinstance(criteria, EligibilityCriteria)
            assert criteria.program_name == program
            assert criteria.income_threshold > 0
            assert len(criteria.required_documents) > 0
        
        # Verify different programs have different thresholds
        snap_threshold = self.plugin.program_criteria['SNAP'].income_threshold
        medicaid_threshold = self.plugin.program_criteria['Medicaid'].income_threshold
        housing_threshold = self.plugin.program_criteria['Housing_Assistance'].income_threshold
        
        assert medicaid_threshold < snap_threshold < housing_threshold


def run_plugin_tests():
    """Run all plugin tests"""
    print("🧪 Running Document Eligibility Agent Plugin Tests")
    print("=" * 65)
    
    test_classes = [
        TestDocumentClassificationPlugin,
        TestDataExtractionPlugin,
        TestEligibilityCalculationPlugin
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        print("-" * 55)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        class_passed = 0
        class_failed = 0
        
        for method_name in test_methods:
            try:
                print(f"  Running {method_name}...", end=" ")
                
                # Setup method if exists
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                method = getattr(test_instance, method_name)
                method()
                
                print("✅ PASSED")
                class_passed += 1
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                class_failed += 1
        
        print(f"  Results: {class_passed} passed, {class_failed} failed")
        total_passed += class_passed
        total_failed += class_failed
    
    print("\n" + "=" * 65)
    print(f"📊 Overall Plugin Test Results: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 All plugin tests passed! Semantic Kernel plugins are working correctly.")
        return True
    else:
        print("⚠️  Some plugin tests failed. Please review plugin implementations.")
        return False


if __name__ == "__main__":
    success = run_plugin_tests()
    exit(0 if success else 1)