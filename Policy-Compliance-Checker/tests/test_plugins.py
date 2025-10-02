"""
Plugin Tests for Policy Compliance Checker
Tests AI-powered analysis plugins with mock responses.
"""
import pytest
import json
import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# Import plugins to test
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.plugins.policy_analysis_plugin import PolicyAnalysisPlugin, PolicyImprovementPlugin


class TestPolicyAnalysisPlugin:
    """Test the AI-powered policy analysis plugin"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.plugin = PolicyAnalysisPlugin(
            azure_openai_deployment="test-deployment",
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key"
        )
    
    def test_init(self):
        """Test plugin initialization"""
        assert self.plugin.deployment == "test-deployment"
        assert self.plugin.endpoint == "https://test.openai.azure.com/"
        assert self.plugin.api_key == "test-key"
        assert self.plugin.kernel is None
    
    @pytest.mark.asyncio
    @patch('src.plugins.policy_analysis_plugin.Kernel')
    @patch('src.plugins.policy_analysis_plugin.AzureChatCompletion')
    async def test_initialize(self, mock_azure_chat, mock_kernel):
        """Test plugin initialization with mocked dependencies"""
        mock_kernel_instance = Mock()
        mock_kernel.return_value = mock_kernel_instance
        
        mock_chat_service = Mock()
        mock_azure_chat.return_value = mock_chat_service
        
        await self.plugin.initialize()
        
        # Verify kernel was created and configured
        mock_kernel.assert_called_once()
        mock_azure_chat.assert_called_once_with(
            deployment_name="test-deployment",
            endpoint="https://test.openai.azure.com/",
            api_key="test-key"
        )
        mock_kernel_instance.add_service.assert_called_once_with(mock_chat_service)
        mock_kernel_instance.add_plugin.assert_called_once_with(self.plugin, plugin_name="PolicyAnalysis")
    
    @pytest.mark.asyncio
    async def test_analyze_policy_compliance_success(self):
        """Test successful policy compliance analysis"""
        # Mock kernel and response
        mock_kernel = Mock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=json.dumps({
            "compliance_score": 85,
            "key_findings": [
                {
                    "category": "structure",
                    "issue": "Missing privacy section",
                    "severity": "high",
                    "recommendation": "Add privacy policy section",
                    "location": "document structure"
                }
            ],
            "missing_sections": ["Privacy Policy", "Terms of Service"],
            "strengths": ["Clear language", "Well organized"],
            "overall_assessment": "Good policy with minor improvements needed"
        }))
        
        mock_kernel.invoke_prompt = AsyncMock(return_value=mock_result)
        self.plugin.kernel = mock_kernel
        
        # Test the function
        document_content = "This is a sample policy document for testing."
        result = await self.plugin.analyze_policy_compliance(
            document_content, "GDPR compliance"
        )
        
        # Verify result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["compliance_score"] == 85
        assert len(result_data["key_findings"]) == 1
        assert "privacy section" in result_data["key_findings"][0]["issue"].lower()
        assert len(result_data["missing_sections"]) == 2
    
    @pytest.mark.asyncio
    async def test_analyze_policy_compliance_error(self):
        """Test policy compliance analysis with error"""
        # Mock kernel that raises an exception
        mock_kernel = Mock()
        mock_kernel.invoke_prompt = AsyncMock(side_effect=Exception("API Error"))
        self.plugin.kernel = mock_kernel
        
        # Test the function
        result = await self.plugin.analyze_policy_compliance(
            "test content", "general compliance"
        )
        
        # Verify error handling
        result_data = json.loads(result)
        assert "error" in result_data
        assert "API Error" in result_data["error"]
        assert result_data["compliance_score"] == 0
    
    @pytest.mark.asyncio
    async def test_compare_policies_success(self):
        """Test successful policy comparison"""
        mock_kernel = Mock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=json.dumps({
            "similarity_score": 75,
            "key_differences": [
                {
                    "category": "data handling",
                    "difference": "Different retention periods",
                    "document1_approach": "30 days retention",
                    "document2_approach": "90 days retention",
                    "recommendation": "Standardize on 60 days"
                }
            ],
            "missing_in_document1": ["Breach notification procedure"],
            "missing_in_document2": ["Data subject rights"],
            "consistency_issues": [],
            "summary": "Documents are similar but have key differences in data handling"
        }))
        
        mock_kernel.invoke_prompt = AsyncMock(return_value=mock_result)
        self.plugin.kernel = mock_kernel
        
        # Test the function
        result = await self.plugin.compare_policies(
            "Document 1 content", "Document 2 content",
            "Privacy Policy v1", "Privacy Policy v2"
        )
        
        # Verify result
        result_data = json.loads(result)
        assert result_data["similarity_score"] == 75
        assert len(result_data["key_differences"]) == 1
        assert "retention periods" in result_data["key_differences"][0]["difference"]
        assert len(result_data["missing_in_document1"]) == 1
        assert len(result_data["missing_in_document2"]) == 1
    
    @pytest.mark.asyncio
    async def test_generate_policy_recommendations_success(self):
        """Test successful policy recommendation generation"""
        mock_kernel = Mock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=json.dumps({
            "policy_outline": {
                "title": "Remote Work Policy",
                "sections": [
                    {
                        "section_name": "Eligibility",
                        "description": "Who can work remotely",
                        "key_points": ["Full-time employees", "Probation completion"]
                    },
                    {
                        "section_name": "Equipment",
                        "description": "Equipment provision and security",
                        "key_points": ["Company laptop", "Secure internet", "VPN access"]
                    }
                ]
            },
            "compliance_considerations": [
                {
                    "area": "Data Security",
                    "requirement": "Secure remote access",
                    "implementation": "Implement VPN and endpoint security"
                }
            ],
            "best_practices": ["Regular check-ins", "Clear communication protocols"],
            "common_pitfalls": ["Lack of boundaries", "Inadequate security measures"],
            "review_schedule": "Annually",
            "stakeholders": ["HR", "IT", "Legal", "Management"]
        }))
        
        mock_kernel.invoke_prompt = AsyncMock(return_value=mock_result)
        self.plugin.kernel = mock_kernel
        
        # Test the function
        result = await self.plugin.generate_policy_recommendations(
            "remote work", "medium", "technology", "GDPR compliance required"
        )
        
        # Verify result
        result_data = json.loads(result)
        assert result_data["policy_outline"]["title"] == "Remote Work Policy"
        assert len(result_data["policy_outline"]["sections"]) == 2
        assert len(result_data["compliance_considerations"]) == 1
        assert len(result_data["best_practices"]) == 2
        assert result_data["review_schedule"] == "Annually"
    
    @pytest.mark.asyncio
    async def test_extract_key_terms_success(self):
        """Test successful key terms extraction"""
        mock_kernel = Mock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=json.dumps({
            "key_terms": [
                {
                    "term": "Personal Data",
                    "definition": "Information relating to identified or identifiable individuals",
                    "context": "Section 2: Data Collection",
                    "importance": "high"
                },
                {
                    "term": "Data Controller",
                    "definition": "Entity that determines purposes and means of processing",
                    "context": "Section 1: Definitions",
                    "importance": "high"
                }
            ],
            "undefined_terms": ["PII", "Data Subject"],
            "acronyms": [
                {
                    "acronym": "GDPR",
                    "expansion": "General Data Protection Regulation",
                    "first_occurrence": "This policy complies with GDPR requirements"
                }
            ],
            "concepts": [
                {
                    "concept": "Right to be Forgotten",
                    "description": "Individual's right to request deletion of personal data",
                    "related_terms": ["Data Deletion", "Erasure"]
                }
            ]
        }))
        
        mock_kernel.invoke_prompt = AsyncMock(return_value=mock_result)
        self.plugin.kernel = mock_kernel
        
        # Test the function
        result = await self.plugin.extract_key_terms(
            "This policy covers personal data handling under GDPR requirements..."
        )
        
        # Verify result
        result_data = json.loads(result)
        assert len(result_data["key_terms"]) == 2
        assert result_data["key_terms"][0]["term"] == "Personal Data"
        assert result_data["key_terms"][0]["importance"] == "high"
        assert len(result_data["undefined_terms"]) == 2
        assert len(result_data["acronyms"]) == 1
        assert result_data["acronyms"][0]["acronym"] == "GDPR"


class TestPolicyImprovementPlugin:
    """Test the policy improvement plugin"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.plugin = PolicyImprovementPlugin(
            azure_openai_deployment="test-deployment",
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key"
        )
    
    def test_init(self):
        """Test plugin initialization"""
        assert self.plugin.deployment == "test-deployment"
        assert self.plugin.endpoint == "https://test.openai.azure.com/"
        assert self.plugin.api_key == "test-key"
        assert self.plugin.kernel is None
    
    @pytest.mark.asyncio
    async def test_suggest_improvements_success(self):
        """Test successful improvement suggestions"""
        mock_kernel = Mock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=json.dumps({
            "clarity_improvements": [
                {
                    "section": "Data Processing",
                    "current_text": "We process data as needed",
                    "suggested_text": "We process personal data only for specified, explicit purposes",
                    "reason": "More specific and GDPR-compliant language"
                }
            ],
            "structure_improvements": [
                {
                    "improvement": "Add table of contents",
                    "rationale": "Improves navigation and accessibility",
                    "implementation": "Create numbered sections with clear headings"
                }
            ],
            "accessibility_improvements": [
                "Use plain language", "Add visual hierarchy", "Include glossary"
            ],
            "legal_considerations": [
                {
                    "area": "Consent",
                    "current_gap": "No clear consent mechanism described",
                    "recommendation": "Add section on how consent is obtained and recorded"
                }
            ],
            "language_improvements": [
                {
                    "issue": "Passive voice overuse", 
                    "examples": ["Data will be processed", "Decisions are made"],
                    "solution": "Use active voice for clarity"
                }
            ]
        }))
        
        mock_kernel.invoke_prompt = AsyncMock(return_value=mock_result)
        self.plugin.kernel = mock_kernel
        
        # Test the function
        result = await self.plugin.suggest_improvements(
            "Sample policy content", "clarity,legal"
        )
        
        # Verify result
        result_data = json.loads(result)
        assert len(result_data["clarity_improvements"]) == 1
        assert "GDPR-compliant" in result_data["clarity_improvements"][0]["reason"]
        assert len(result_data["structure_improvements"]) == 1
        assert len(result_data["accessibility_improvements"]) == 3
        assert len(result_data["legal_considerations"]) == 1
        assert "consent" in result_data["legal_considerations"][0]["current_gap"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_implementation_checklist_success(self):
        """Test successful implementation checklist generation"""
        mock_kernel = Mock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=json.dumps({
            "pre_implementation": [
                {
                    "task": "Legal review of policy",
                    "responsible_party": "Legal team",
                    "timeline": "2 weeks before implementation",
                    "dependencies": ["Policy draft completion"]
                },
                {
                    "task": "Stakeholder approval",
                    "responsible_party": "Policy owner",
                    "timeline": "1 week before implementation",
                    "dependencies": ["Legal review completion"]
                }
            ],
            "implementation_steps": [
                {
                    "step": "Publish policy on company intranet",
                    "details": "Upload policy to accessible location with versioning",
                    "success_criteria": "Policy is searchable and accessible to all employees",
                    "resources_needed": ["IT support", "Communications team"]
                },
                {
                    "step": "Manager briefings",
                    "details": "Brief all managers on policy requirements and their responsibilities",
                    "success_criteria": "All managers complete briefing and acknowledge understanding",
                    "resources_needed": ["Training materials", "Meeting time"]
                }
            ],
            "communication_plan": [
                {
                    "audience": "All employees",
                    "message": "New privacy policy effective immediately",
                    "method": "Company-wide email and intranet announcement",
                    "timing": "Day of implementation"
                },
                {
                    "audience": "Managers",
                    "message": "Manager responsibilities under new policy",
                    "method": "Manager meeting and follow-up email",
                    "timing": "1 day before general announcement"
                }
            ],
            "training_requirements": [
                {
                    "topic": "Policy overview and requirements",
                    "audience": "All employees",
                    "format": "Online training module",
                    "frequency": "Once, with annual refresher"
                },
                {
                    "topic": "Manager-specific requirements",
                    "audience": "All managers",
                    "format": "In-person workshop",
                    "frequency": "Once, with updates as needed"
                }
            ],
            "monitoring_and_review": [
                {
                    "metric": "Policy compliance rate",
                    "frequency": "Quarterly",
                    "responsible_party": "Compliance team",
                    "escalation": "Report to executive team if compliance drops below 90%"
                },
                {
                    "metric": "Employee understanding assessment",
                    "frequency": "Annually",
                    "responsible_party": "HR team",
                    "escalation": "Additional training if assessment scores below 80%"
                }
            ]
        }))
        
        mock_kernel.invoke_prompt = AsyncMock(return_value=mock_result)
        self.plugin.kernel = mock_kernel
        
        # Test the function
        result = await self.plugin.generate_implementation_checklist(
            "Data Privacy Policy",
            "Comprehensive policy for handling personal data...",
            "Medium-sized tech company"
        )
        
        # Verify result
        result_data = json.loads(result)
        assert len(result_data["pre_implementation"]) == 2
        assert "Legal review" in result_data["pre_implementation"][0]["task"]
        assert len(result_data["implementation_steps"]) == 2
        assert "policy" in result_data["implementation_steps"][0]["details"].lower()
        assert len(result_data["communication_plan"]) == 2
        assert len(result_data["training_requirements"]) == 2
        assert len(result_data["monitoring_and_review"]) == 2
    
    @pytest.mark.asyncio
    async def test_plugin_error_handling(self):
        """Test error handling in improvement plugin"""
        mock_kernel = Mock()
        mock_kernel.invoke_prompt = AsyncMock(side_effect=Exception("Network error"))
        self.plugin.kernel = mock_kernel
        
        # Test error handling
        result = await self.plugin.suggest_improvements("test content")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "Network error" in result_data["error"]
        assert result_data["clarity_improvements"] == []
        assert result_data["structure_improvements"] == []


def run_plugin_tests():
    """Run all plugin tests manually"""
    print("🔌 Running Policy Compliance Checker Plugin Tests")
    print("=" * 60)
    
    test_classes = [
        TestPolicyAnalysisPlugin,
        TestPolicyImprovementPlugin
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    # Set up event loop for async tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        for test_class in test_classes:
            print(f"\n📋 Testing {test_class.__name__}")
            print("-" * 40)
            
            # Get all test methods
            test_methods = [method for method in dir(test_class) if method.startswith('test_')]
            
            for method_name in test_methods:
                total_tests += 1
                
                try:
                    # Create instance and run setup
                    instance = test_class()
                    instance.setup_method()
                    
                    # Run the test (handle async methods)
                    test_method = getattr(instance, method_name)
                    if asyncio.iscoroutinefunction(test_method):
                        loop.run_until_complete(test_method())
                    else:
                        test_method()
                    
                    print(f"  ✅ {method_name}")
                    passed_tests += 1
                    
                except Exception as e:
                    print(f"  ❌ {method_name} - FAILED: {str(e)}")
                    failed_tests.append((test_class.__name__, method_name, str(e)))
    
    finally:
        loop.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PLUGIN TEST SUMMARY")
    print("=" * 60)
    print(f"🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for class_name, method_name, error in failed_tests:
            print(f"   • {class_name}.{method_name}")
            print(f"     Error: {error}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL PLUGIN TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {len(failed_tests)} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_plugin_tests()
    
    print("\n💡 To run with pytest framework:")
    print("   pytest tests/test_plugins.py -v")
    print("   pytest tests/test_plugins.py::TestPolicyAnalysisPlugin::test_analyze_policy_compliance_success -v")
    
    exit(0 if success else 1)