"""
Semantic Kernel plugins for document processing orchestration
"""
import logging
from typing import List, Dict, Any, Optional
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from ..models.document_types import DocumentType, ExtractedData, EligibilityAssessment, EligibilityCriteria


class DocumentClassificationPlugin:
    """Semantic Kernel plugin for document classification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @kernel_function(
        description="Classify document type based on content and metadata",
        name="classify_document_type"
    )
    def classify_document_type(self, file_name: str, extracted_text: str = "") -> str:
        """
        Classify document type using AI analysis
        
        Args:
            file_name: Name of the document file
            extracted_text: OCR extracted text content
            
        Returns:
            Document type classification
        """
        try:
            # Simple rule-based classification (can be enhanced with AI)
            file_name_lower = file_name.lower()
            text_lower = extracted_text.lower()
            
            # Income verification documents
            income_keywords = ['pay', 'stub', 'salary', 'wage', 'income', 'tax', 'w2', '1099', 'employment']
            if any(keyword in file_name_lower or keyword in text_lower for keyword in income_keywords):
                return DocumentType.INCOME_VERIFICATION.value
            
            # Medical records
            medical_keywords = ['medical', 'health', 'insurance', 'patient', 'doctor', 'prescription', 'treatment']
            if any(keyword in file_name_lower or keyword in text_lower for keyword in medical_keywords):
                return DocumentType.MEDICAL_RECORD.value
            
            # Utility bills
            utility_keywords = ['utility', 'electric', 'gas', 'water', 'bill', 'energy', 'power']
            if any(keyword in file_name_lower or keyword in text_lower for keyword in utility_keywords):
                return DocumentType.UTILITY_BILL.value
            
            # Identity documents
            identity_keywords = ['license', 'id', 'passport', 'ssn', 'social security', 'birth certificate']
            if any(keyword in file_name_lower or keyword in text_lower for keyword in identity_keywords):
                return DocumentType.IDENTITY_DOCUMENT.value
            
            # Bank statements
            bank_keywords = ['bank', 'statement', 'account', 'balance', 'transaction', 'deposit']
            if any(keyword in file_name_lower or keyword in text_lower for keyword in bank_keywords):
                return DocumentType.BANK_STATEMENT.value
            
            # Housing documents
            housing_keywords = ['lease', 'rent', 'mortgage', 'housing', 'property', 'landlord']
            if any(keyword in file_name_lower or keyword in text_lower for keyword in housing_keywords):
                return DocumentType.HOUSING_DOCUMENT.value
            
            return DocumentType.UNKNOWN.value
            
        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}")
            return DocumentType.UNKNOWN.value
    
    @kernel_function(
        description="Validate document classification confidence",
        name="validate_classification"
    )
    def validate_classification(self, classification: str, extracted_fields: Dict[str, Any]) -> float:
        """
        Validate classification confidence based on extracted fields
        
        Args:
            classification: Predicted document type
            extracted_fields: Fields extracted from document
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            doc_type = DocumentType(classification)
            confidence = 0.5  # Base confidence
            
            # Boost confidence based on expected fields for document type
            if doc_type == DocumentType.INCOME_VERIFICATION:
                if any('income' in key or 'amount' in key or 'salary' in key for key in extracted_fields.keys()):
                    confidence += 0.3
                if any('date' in key or 'period' in key for key in extracted_fields.keys()):
                    confidence += 0.2
                    
            elif doc_type == DocumentType.MEDICAL_RECORD:
                if any('patient' in key or 'insurance' in key for key in extracted_fields.keys()):
                    confidence += 0.3
                if any('date' in key or 'visit' in key for key in extracted_fields.keys()):
                    confidence += 0.2
                    
            elif doc_type == DocumentType.UTILITY_BILL:
                if any('address' in key for key in extracted_fields.keys()):
                    confidence += 0.3
                if any('amount' in key or 'bill' in key for key in extracted_fields.keys()):
                    confidence += 0.2
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error validating classification: {str(e)}")
            return 0.0


class DataExtractionPlugin:
    """Semantic Kernel plugin for data extraction and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @kernel_function(
        description="Extract key information from document text",
        name="extract_key_information"
    )
    def extract_key_information(self, document_type: str, text_content: str) -> Dict[str, Any]:
        """
        Extract key information based on document type
        
        Args:
            document_type: Type of document
            text_content: Full text content of document
            
        Returns:
            Dictionary of extracted key-value pairs
        """
        try:
            doc_type = DocumentType(document_type)
            extracted_info = {}
            
            if doc_type == DocumentType.INCOME_VERIFICATION:
                extracted_info = self._extract_income_info(text_content)
            elif doc_type == DocumentType.MEDICAL_RECORD:
                extracted_info = self._extract_medical_info(text_content)
            elif doc_type == DocumentType.UTILITY_BILL:
                extracted_info = self._extract_utility_info(text_content)
            elif doc_type == DocumentType.IDENTITY_DOCUMENT:
                extracted_info = self._extract_identity_info(text_content)
            
            return extracted_info
            
        except Exception as e:
            self.logger.error(f"Error extracting information: {str(e)}")
            return {}
    
    def _extract_income_info(self, text: str) -> Dict[str, Any]:
        """Extract income-specific information"""
        info = {}
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            # Look for income amounts - prioritize gross pay over net pay
            import re
            if 'gross pay' in line_lower:
                # Look for dollar amounts with commas and decimals
                amounts = re.findall(r'\$([0-9,]+\.[0-9]{2})', line)
                if amounts:
                    # Take the largest amount found (likely the main pay amount)
                    largest_amount = max(amounts, key=lambda x: float(x.replace(',', '')))
                    info['income_amount'] = largest_amount
            elif any(keyword in line_lower for keyword in ['net pay', 'salary', 'total income']) and 'income_amount' not in info:
                # Look for dollar amounts with commas and decimals (only if gross pay not found yet)
                amounts = re.findall(r'\$([0-9,]+\.[0-9]{2})', line)
                if amounts:
                    # Take the largest amount found (likely the main pay amount)
                    largest_amount = max(amounts, key=lambda x: float(x.replace(',', '')))
                    info['income_amount'] = largest_amount
            
            # Look for employer information
            if 'employer' in line_lower or 'company' in line_lower:
                info['employer'] = line.strip()
            
            # Look for pay period
            if any(keyword in line_lower for keyword in ['pay period', 'frequency', 'bi-weekly', 'monthly']):
                info['pay_period'] = line.strip()
        
        return info
    
    def _extract_medical_info(self, text: str) -> Dict[str, Any]:
        """Extract medical record information"""
        info = {}
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'patient' in line_lower and 'name' in line_lower:
                info['patient_name'] = line.strip()
            elif 'insurance' in line_lower:
                info['insurance_info'] = line.strip()
            elif 'date' in line_lower:
                info['visit_date'] = line.strip()
        
        return info
    
    def _extract_utility_info(self, text: str) -> Dict[str, Any]:
        """Extract utility bill information"""
        info = {}
        lines = text.split('\n')
        
        found_address_section = False
        for i, line in enumerate(lines):
            line_lower = line.lower()
            line_stripped = line.strip()
            
            # Look for service address section
            if 'service address' in line_lower or 'billing address' in line_lower:
                found_address_section = True
                continue
            
            # If we found address section, capture the next few non-empty lines as address
            if found_address_section and line_stripped:
                # Check if this looks like an address (contains numbers and letters)
                import re
                if re.search(r'\d+.*[A-Za-z]', line_stripped):
                    info['service_address'] = line_stripped
                    found_address_section = False  # Stop after first address line
            
            # Look for amount due
            if 'amount due' in line_lower or 'total' in line_lower:
                import re
                amounts = re.findall(r'\$([0-9,]+\.[0-9]{2})', line)
                if amounts:
                    info['amount_due'] = amounts[0]
        
        return info
    
    def _extract_identity_info(self, text: str) -> Dict[str, Any]:
        """Extract identity document information"""
        info = {}
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'name' in line_lower:
                info['full_name'] = line.strip()
            elif 'address' in line_lower:
                info['address'] = line.strip()
            elif 'number' in line_lower:
                info['id_number'] = line.strip()
        
        return info
    
    @kernel_function(
        description="Validate extracted data quality",
        name="validate_extraction_quality"
    )
    def validate_extraction_quality(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate quality of extracted data
        
        Args:
            extracted_data: Dictionary of extracted data
            
        Returns:
            Validation results with quality score and issues
        """
        try:
            validation_result = {
                'quality_score': 0.0,
                'issues': [],
                'completeness': 0.0
            }
            
            total_fields = len(extracted_data)
            if total_fields == 0:
                validation_result['issues'].append("No data extracted")
                return validation_result
            
            # Check for empty or invalid values
            valid_fields = 0
            for key, value in extracted_data.items():
                if value and str(value).strip():
                    valid_fields += 1
                else:
                    validation_result['issues'].append(f"Empty or invalid value for {key}")
            
            validation_result['completeness'] = valid_fields / total_fields
            validation_result['quality_score'] = validation_result['completeness']
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating extraction quality: {str(e)}")
            return {'quality_score': 0.0, 'issues': [str(e)], 'completeness': 0.0}


class EligibilityCalculationPlugin:
    """Semantic Kernel plugin for eligibility determination"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Define eligibility criteria for different programs
        self.program_criteria = {
            'SNAP': EligibilityCriteria(
                program_name='SNAP',
                income_threshold=2000.0,  # Monthly income threshold
                household_size_factor=True,
                required_documents=[
                    DocumentType.INCOME_VERIFICATION,
                    DocumentType.IDENTITY_DOCUMENT,
                    DocumentType.UTILITY_BILL
                ]
            ),
            'Medicaid': EligibilityCriteria(
                program_name='Medicaid',
                income_threshold=1500.0,
                household_size_factor=True,
                required_documents=[
                    DocumentType.INCOME_VERIFICATION,
                    DocumentType.IDENTITY_DOCUMENT,
                    DocumentType.MEDICAL_RECORD
                ]
            ),
            'Housing_Assistance': EligibilityCriteria(
                program_name='Housing_Assistance',
                income_threshold=3000.0,
                household_size_factor=True,
                required_documents=[
                    DocumentType.INCOME_VERIFICATION,
                    DocumentType.IDENTITY_DOCUMENT,
                    DocumentType.HOUSING_DOCUMENT,
                    DocumentType.UTILITY_BILL
                ]
            )
        }
    
    @kernel_function(
        description="Calculate eligibility for benefit programs",
        name="calculate_eligibility"
    )
    def calculate_eligibility(
        self, 
        program_name: str, 
        monthly_income: float, 
        household_size: int,
        available_documents: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate eligibility for a specific program
        
        Args:
            program_name: Name of benefit program
            monthly_income: Applicant's monthly income
            household_size: Number of people in household
            available_documents: List of available document types
            
        Returns:
            Eligibility assessment results
        """
        try:
            if program_name not in self.program_criteria:
                return {
                    'eligible': False,
                    'reason': f"Unknown program: {program_name}",
                    'confidence': 0.0
                }
            
            criteria = self.program_criteria[program_name]
            assessment = {
                'eligible': True,
                'reason': '',
                'confidence': 1.0,
                'missing_documents': [],
                'income_assessment': {}
            }
            
            # Check income eligibility
            adjusted_threshold = criteria.income_threshold
            if criteria.household_size_factor:
                # Adjust threshold based on household size
                adjusted_threshold = criteria.income_threshold * (1 + (household_size - 1) * 0.3)
            
            if monthly_income > adjusted_threshold:
                assessment['eligible'] = False
                assessment['reason'] = f"Income ${monthly_income:.2f} exceeds threshold ${adjusted_threshold:.2f}"
                assessment['confidence'] = 0.9
            
            assessment['income_assessment'] = {
                'monthly_income': monthly_income,
                'threshold': adjusted_threshold,
                'household_size': household_size,
                'income_eligible': monthly_income <= adjusted_threshold
            }
            
            # Check required documents
            available_doc_types = [DocumentType(doc) for doc in available_documents if doc in [dt.value for dt in DocumentType]]
            missing_docs = [doc for doc in criteria.required_documents if doc not in available_doc_types]
            
            if missing_docs:
                assessment['missing_documents'] = [doc.value for doc in missing_docs]
                if assessment['eligible']:  # Only change if still eligible
                    assessment['eligible'] = False
                    assessment['reason'] = f"Missing required documents: {', '.join([doc.value for doc in missing_docs])}"
                    assessment['confidence'] = 0.8
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error calculating eligibility: {str(e)}")
            return {
                'eligible': False,
                'reason': f"Error in calculation: {str(e)}",
                'confidence': 0.0
            }
    
    @kernel_function(
        description="Generate eligibility recommendations",
        name="generate_recommendations"
    )
    def generate_recommendations(
        self, 
        assessment_results: Dict[str, Any],
        applicant_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations based on eligibility assessment
        
        Args:
            assessment_results: Results from eligibility calculation
            applicant_data: Additional applicant information
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            if assessment_results.get('eligible', False):
                recommendations.append("✅ You appear to be eligible for this program")
                recommendations.append("📋 Please submit your application with all required documents")
                recommendations.append("⏱️ Processing typically takes 5-10 business days")
            else:
                reason = assessment_results.get('reason', '')
                
                if 'income' in reason.lower():
                    recommendations.append("❌ Current income exceeds program limits")
                    recommendations.append("💡 Consider applying for other assistance programs")
                    recommendations.append("📊 Income limits may change annually - check back later")
                
                if 'missing' in reason.lower():
                    missing_docs = assessment_results.get('missing_documents', [])
                    recommendations.append("📄 Additional documents required:")
                    for doc in missing_docs:
                        recommendations.append(f"   • {doc.replace('_', ' ').title()}")
                    recommendations.append("📧 Please email additional documents or visit our office")
            
            # General recommendations
            recommendations.append("📞 Contact our office if you have questions: (555) 123-4567")
            recommendations.append("🌐 Visit our website for more information and resources")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return ["❌ Error generating recommendations. Please contact our office for assistance."]