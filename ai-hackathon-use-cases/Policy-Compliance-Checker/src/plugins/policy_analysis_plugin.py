"""
Policy Compliance Checker - Semantic Kernel Plugins
Provides AI-powered analysis and recommendations using semantic kernel.
"""
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from typing import Annotated, Dict, List, Optional, Any
import json
import asyncio


class PolicyAnalysisPlugin:
    """AI-powered policy analysis using semantic kernel"""
    
    def __init__(self, azure_openai_deployment: str, azure_openai_endpoint: str, azure_openai_api_key: str):
        self.deployment = azure_openai_deployment
        self.endpoint = azure_openai_endpoint
        self.api_key = azure_openai_api_key
        self.kernel = None
        self.chat_history = ChatHistory()
    
    async def initialize(self):
        """Initialize the semantic kernel"""
        self.kernel = Kernel()
        
        # Add Azure OpenAI chat service
        chat_service = AzureChatCompletion(
            deployment_name=self.deployment,
            endpoint=self.endpoint,
            api_key=self.api_key
        )
        self.kernel.add_service(chat_service)
        
        # Add this plugin to the kernel
        self.kernel.add_plugin(self, plugin_name="PolicyAnalysis")
    
    @kernel_function(
        description="Analyze policy document for compliance gaps and provide recommendations",
        name="analyze_policy_compliance"
    )
    async def analyze_policy_compliance(
        self,
        document_content: Annotated[str, "The full text content of the policy document to analyze"],
        compliance_requirements: Annotated[str, "Specific compliance requirements or standards to check against"] = "general best practices"
    ) -> Annotated[str, "JSON string containing compliance analysis and recommendations"]:
        """Analyze a policy document for compliance issues"""
        
        prompt = f"""
        You are an expert policy compliance analyst. Analyze the following policy document for compliance issues and provide detailed recommendations.

        Policy Document:
        {document_content[:4000]}  # Limit content to avoid token limits

        Compliance Requirements: {compliance_requirements}

        Please provide analysis in the following JSON format:
        {{
            "compliance_score": <score from 0-100>,
            "key_findings": [
                {{
                    "category": "<category>",
                    "issue": "<description>",
                    "severity": "<critical|high|medium|low>",
                    "recommendation": "<specific recommendation>",
                    "location": "<section or area>"
                }}
            ],
            "missing_sections": [
                "<list of important sections that should be added>"
            ],
            "strengths": [
                "<list of policy strengths>"
            ],
            "overall_assessment": "<summary of overall compliance status>"
        }}

        Focus on:
        1. Legal compliance requirements
        2. Security and data protection policies
        3. Accessibility considerations
        4. Clarity and consistency of language
        5. Completeness of policy coverage
        """
        
        try:
            # Use the kernel to get AI response
            result = await self.kernel.invoke_prompt(prompt)
            return str(result)
        except Exception as e:
            return json.dumps({
                "error": f"Analysis failed: {str(e)}",
                "compliance_score": 0,
                "key_findings": [],
                "missing_sections": [],
                "strengths": [],
                "overall_assessment": "Unable to complete analysis due to error"
            })
    
    @kernel_function(
        description="Compare two policy documents and identify differences",
        name="compare_policies"
    )
    async def compare_policies(
        self,
        document1_content: Annotated[str, "Content of the first policy document"],
        document2_content: Annotated[str, "Content of the second policy document"],
        document1_title: Annotated[str, "Title of the first document"] = "Document 1",
        document2_title: Annotated[str, "Title of the second document"] = "Document 2"
    ) -> Annotated[str, "JSON string containing comparison analysis"]:
        """Compare two policy documents and identify key differences"""
        
        prompt = f"""
        You are comparing two policy documents to identify differences, inconsistencies, and gaps.

        {document1_title}:
        {document1_content[:2000]}

        {document2_title}:
        {document2_content[:2000]}

        Provide comparison results in JSON format:
        {{
            "similarity_score": <0-100>,
            "key_differences": [
                {{
                    "category": "<category>",
                    "difference": "<description>",
                    "document1_approach": "<how document 1 handles this>",
                    "document2_approach": "<how document 2 handles this>",
                    "recommendation": "<suggested approach>"
                }}
            ],
            "missing_in_document1": ["<items present in doc2 but not doc1>"],
            "missing_in_document2": ["<items present in doc1 but not doc2>"],
            "consistency_issues": [
                {{
                    "issue": "<description>",
                    "impact": "<potential impact>",
                    "solution": "<recommended solution>"
                }}
            ],
            "summary": "<overall comparison summary>"
        }}
        """
        
        try:
            result = await self.kernel.invoke_prompt(prompt)
            return str(result)
        except Exception as e:
            return json.dumps({
                "error": f"Comparison failed: {str(e)}",
                "similarity_score": 0,
                "key_differences": [],
                "missing_in_document1": [],
                "missing_in_document2": [],
                "consistency_issues": [],
                "summary": "Unable to complete comparison due to error"
            })
    
    @kernel_function(
        description="Generate policy recommendations based on best practices",
        name="generate_policy_recommendations"
    )
    async def generate_policy_recommendations(
        self,
        policy_type: Annotated[str, "Type of policy (e.g., 'remote work', 'data privacy', 'code of conduct')"],
        organization_size: Annotated[str, "Organization size (small/medium/large)"] = "medium",
        industry: Annotated[str, "Industry or sector"] = "general",
        specific_requirements: Annotated[str, "Any specific requirements or constraints"] = "none"
    ) -> Annotated[str, "JSON string containing policy recommendations"]:
        """Generate policy recommendations based on type and organization context"""
        
        prompt = f"""
        Generate comprehensive policy recommendations for the following context:

        Policy Type: {policy_type}
        Organization Size: {organization_size}
        Industry: {industry}
        Specific Requirements: {specific_requirements}

        Provide recommendations in JSON format:
        {{
            "policy_outline": {{
                "title": "<suggested policy title>",
                "sections": [
                    {{
                        "section_name": "<section name>",
                        "description": "<what this section should cover>",
                        "key_points": ["<list of key points to include>"]
                    }}
                ]
            }},
            "compliance_considerations": [
                {{
                    "area": "<compliance area>",
                    "requirement": "<requirement description>",
                    "implementation": "<how to implement>"
                }}
            ],
            "best_practices": [
                "<list of industry best practices to follow>"
            ],
            "common_pitfalls": [
                "<list of common mistakes to avoid>"
            ],
            "review_schedule": "<recommended review frequency>",
            "stakeholders": ["<list of who should be involved>"]
        }}
        """
        
        try:
            result = await self.kernel.invoke_prompt(prompt)
            return str(result)
        except Exception as e:
            return json.dumps({
                "error": f"Recommendation generation failed: {str(e)}",
                "policy_outline": {"title": "", "sections": []},
                "compliance_considerations": [],
                "best_practices": [],
                "common_pitfalls": [],
                "review_schedule": "",
                "stakeholders": []
            })
    
    @kernel_function(
        description="Extract key terms and definitions from policy document",
        name="extract_key_terms"
    )
    async def extract_key_terms(
        self,
        document_content: Annotated[str, "The policy document content to analyze"]
    ) -> Annotated[str, "JSON string containing extracted terms and definitions"]:
        """Extract important terms and their definitions from a policy document"""
        
        prompt = f"""
        Analyze the following policy document and extract key terms, definitions, and important concepts.

        Document Content:
        {document_content[:3000]}

        Extract information in JSON format:
        {{
            "key_terms": [
                {{
                    "term": "<term>",
                    "definition": "<definition or explanation>",
                    "context": "<where it appears in the document>",
                    "importance": "<high|medium|low>"
                }}
            ],
            "undefined_terms": [
                "<terms that are used but not clearly defined>"
            ],
            "acronyms": [
                {{
                    "acronym": "<acronym>",
                    "expansion": "<full form>",
                    "first_occurrence": "<context where first used>"
                }}
            ],
            "concepts": [
                {{
                    "concept": "<concept name>",
                    "description": "<brief description>",
                    "related_terms": ["<related terms>"]
                }}
            ]
        }}
        """
        
        try:
            result = await self.kernel.invoke_prompt(prompt)
            return str(result)
        except Exception as e:
            return json.dumps({
                "error": f"Term extraction failed: {str(e)}",
                "key_terms": [],
                "undefined_terms": [],
                "acronyms": [],
                "concepts": []
            })


class PolicyImprovementPlugin:
    """Plugin for generating policy improvements and suggestions"""
    
    def __init__(self, azure_openai_deployment: str, azure_openai_endpoint: str, azure_openai_api_key: str):
        self.deployment = azure_openai_deployment
        self.endpoint = azure_openai_endpoint
        self.api_key = azure_openai_api_key
        self.kernel = None
    
    async def initialize(self):
        """Initialize the semantic kernel"""
        self.kernel = Kernel()
        
        # Add Azure OpenAI chat service
        chat_service = AzureChatCompletion(
            deployment_name=self.deployment,
            endpoint=self.endpoint,
            api_key=self.api_key
        )
        self.kernel.add_service(chat_service)
        
        # Add this plugin to the kernel
        self.kernel.add_plugin(self, plugin_name="PolicyImprovement")
    
    @kernel_function(
        description="Suggest improvements for policy clarity and effectiveness",
        name="suggest_improvements"
    )
    async def suggest_improvements(
        self,
        document_content: Annotated[str, "The policy document content to improve"],
        focus_areas: Annotated[str, "Specific areas to focus on (clarity, accessibility, legal, etc.)"] = "all"
    ) -> Annotated[str, "JSON string containing improvement suggestions"]:
        """Suggest specific improvements for a policy document"""
        
        prompt = f"""
        Review the following policy document and suggest specific improvements.

        Document Content:
        {document_content[:3000]}

        Focus Areas: {focus_areas}

        Provide suggestions in JSON format:
        {{
            "clarity_improvements": [
                {{
                    "section": "<section name>",
                    "current_text": "<current problematic text>",
                    "suggested_text": "<improved version>",
                    "reason": "<why this is better>"
                }}
            ],
            "structure_improvements": [
                {{
                    "improvement": "<structural change>",
                    "rationale": "<why this helps>",
                    "implementation": "<how to implement>"
                }}
            ],
            "accessibility_improvements": [
                "<suggestions for making policy more accessible>"
            ],
            "legal_considerations": [
                {{
                    "area": "<legal area>",
                    "current_gap": "<what's missing>",
                    "recommendation": "<what to add>"
                }}
            ],
            "language_improvements": [
                {{
                    "issue": "<language issue>",
                    "examples": ["<examples of the issue>"],
                    "solution": "<how to fix>"
                }}
            ]
        }}
        """
        
        try:
            result = await self.kernel.invoke_prompt(prompt)
            return str(result)
        except Exception as e:
            return json.dumps({
                "error": f"Improvement suggestion failed: {str(e)}",
                "clarity_improvements": [],
                "structure_improvements": [],
                "accessibility_improvements": [],
                "legal_considerations": [],
                "language_improvements": []
            })
    
    @kernel_function(
        description="Generate a policy implementation checklist",
        name="generate_implementation_checklist"
    )
    async def generate_implementation_checklist(
        self,
        policy_title: Annotated[str, "Title of the policy"],
        policy_content: Annotated[str, "Content of the policy document"],
        organization_context: Annotated[str, "Context about the organization"] = "general organization"
    ) -> Annotated[str, "JSON string containing implementation checklist"]:
        """Generate a checklist for implementing a policy"""
        
        prompt = f"""
        Create a comprehensive implementation checklist for the following policy:

        Policy: {policy_title}
        Context: {organization_context}

        Policy Content (abbreviated):
        {policy_content[:2000]}

        Generate checklist in JSON format:
        {{
            "pre_implementation": [
                {{
                    "task": "<task description>",
                    "responsible_party": "<who should do this>",
                    "timeline": "<when to complete>",
                    "dependencies": ["<what needs to be done first>"]
                }}
            ],
            "implementation_steps": [
                {{
                    "step": "<step description>",
                    "details": "<implementation details>",
                    "success_criteria": "<how to know it's done>",
                    "resources_needed": ["<resources required>"]
                }}
            ],
            "communication_plan": [
                {{
                    "audience": "<target audience>",
                    "message": "<key message>",
                    "method": "<communication method>",
                    "timing": "<when to communicate>"
                }}
            ],
            "training_requirements": [
                {{
                    "topic": "<training topic>",
                    "audience": "<who needs training>",
                    "format": "<training format>",
                    "frequency": "<how often>"
                }}
            ],
            "monitoring_and_review": [
                {{
                    "metric": "<what to measure>",
                    "frequency": "<how often>",
                    "responsible_party": "<who monitors>",
                    "escalation": "<when to escalate>"
                }}
            ]
        }}
        """
        
        try:
            result = await self.kernel.invoke_prompt(prompt)
            return str(result)
        except Exception as e:
            return json.dumps({
                "error": f"Checklist generation failed: {str(e)}",
                "pre_implementation": [],
                "implementation_steps": [],
                "communication_plan": [],
                "training_requirements": [],
                "monitoring_and_review": []
            })