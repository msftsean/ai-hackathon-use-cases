"""
Policy Compliance Checker - Main Application
Orchestrates document parsing, compliance checking, and AI analysis.
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.core.document_parser import DocumentParser, PolicyDocument
from src.core.compliance_engine import ComplianceRulesEngine, ComplianceReport
from src.plugins.policy_analysis_plugin import PolicyAnalysisPlugin, PolicyImprovementPlugin


class PolicyComplianceChecker:
    """Main application class for policy compliance checking"""
    
    def __init__(self, 
                 azure_openai_deployment: Optional[str] = None,
                 azure_openai_endpoint: Optional[str] = None, 
                 azure_openai_api_key: Optional[str] = None):
        
        self.document_parser = DocumentParser()
        self.compliance_engine = ComplianceRulesEngine()
        
        # Initialize AI plugins if Azure OpenAI credentials are provided
        self.ai_analysis_enabled = all([azure_openai_deployment, azure_openai_endpoint, azure_openai_api_key])
        
        if self.ai_analysis_enabled:
            self.policy_analysis_plugin = PolicyAnalysisPlugin(
                azure_openai_deployment, azure_openai_endpoint, azure_openai_api_key
            )
            self.policy_improvement_plugin = PolicyImprovementPlugin(
                azure_openai_deployment, azure_openai_endpoint, azure_openai_api_key
            )
        else:
            self.policy_analysis_plugin = None
            self.policy_improvement_plugin = None
    
    async def initialize(self):
        """Initialize the application and AI plugins"""
        if self.ai_analysis_enabled:
            await self.policy_analysis_plugin.initialize()
            await self.policy_improvement_plugin.initialize()
        
        print("✓ Policy Compliance Checker initialized successfully")
        if self.ai_analysis_enabled:
            print("✓ AI-powered analysis enabled")
        else:
            print("ℹ AI analysis disabled - provide Azure OpenAI credentials to enable")
    
    def load_compliance_rules(self, rules_file_path: str) -> None:
        """Load compliance rules from a JSON file"""
        if not os.path.exists(rules_file_path):
            raise FileNotFoundError(f"Rules file not found: {rules_file_path}")
        
        self.compliance_engine.load_rules_from_file(rules_file_path)
        print(f"✓ Loaded {len(self.compliance_engine.rules)} compliance rules")
    
    def parse_document(self, document_path: str) -> PolicyDocument:
        """Parse a policy document"""
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        document = self.document_parser.parse_document(document_path)
        print(f"✓ Parsed document: {document.title}")
        print(f"  - {len(document.sections)} sections found")
        print(f"  - {document.metadata['word_count']} words")
        
        return document
    
    def check_compliance(self, document: PolicyDocument, selected_rules: Optional[List[str]] = None) -> ComplianceReport:
        """Check document compliance against loaded rules"""
        if not self.compliance_engine.rules:
            raise ValueError("No compliance rules loaded. Use load_compliance_rules() first.")
        
        report = self.compliance_engine.check_compliance(document, selected_rules)
        
        print(f"\n📊 Compliance Check Results for '{document.title}':")
        print(f"   Compliance Score: {report.compliance_score:.1f}%")
        print(f"   Total Violations: {len(report.violations)}")
        print(f"   Rules Checked: {report.total_rules_checked}")
        
        if report.violations:
            print("\n🚨 Violations Found:")
            for violation in report.violations[:5]:  # Show first 5
                print(f"   • [{violation.level.value.upper()}] {violation.description}")
                if len(report.violations) > 5:
                    print(f"   ... and {len(report.violations) - 5} more")
                    break
        else:
            print("✅ No violations found!")
        
        return report
    
    async def ai_analyze_document(self, document: PolicyDocument, requirements: str = "general best practices") -> Dict[str, Any]:
        """Perform AI-powered analysis of the document"""
        if not self.ai_analysis_enabled:
            raise ValueError("AI analysis not available. Provide Azure OpenAI credentials.")
        
        print("🤖 Running AI analysis...")
        
        try:
            result = await self.policy_analysis_plugin.analyze_policy_compliance(
                document.content, requirements
            )
            
            # Parse JSON response
            analysis = json.loads(result)
            
            print(f"✓ AI Analysis completed")
            print(f"  AI Compliance Score: {analysis.get('compliance_score', 'N/A')}%")
            print(f"  Key Findings: {len(analysis.get('key_findings', []))}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ AI analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def ai_suggest_improvements(self, document: PolicyDocument, focus_areas: str = "all") -> Dict[str, Any]:
        """Get AI-powered improvement suggestions"""
        if not self.ai_analysis_enabled:
            raise ValueError("AI analysis not available. Provide Azure OpenAI credentials.")
        
        print("💡 Generating improvement suggestions...")
        
        try:
            result = await self.policy_improvement_plugin.suggest_improvements(
                document.content, focus_areas
            )
            
            suggestions = json.loads(result)
            
            print("✓ Improvement suggestions generated")
            
            return suggestions
            
        except Exception as e:
            print(f"❌ Suggestion generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def ai_compare_documents(self, doc1: PolicyDocument, doc2: PolicyDocument) -> Dict[str, Any]:
        """Compare two documents using AI"""
        if not self.ai_analysis_enabled:
            raise ValueError("AI analysis not available. Provide Azure OpenAI credentials.")
        
        print(f"🔄 Comparing '{doc1.title}' with '{doc2.title}'...")
        
        try:
            result = await self.policy_analysis_plugin.compare_policies(
                doc1.content, doc2.content, doc1.title, doc2.title
            )
            
            comparison = json.loads(result)
            
            print(f"✓ Document comparison completed")
            print(f"  Similarity Score: {comparison.get('similarity_score', 'N/A')}%")
            
            return comparison
            
        except Exception as e:
            print(f"❌ Document comparison failed: {str(e)}")
            return {"error": str(e)}
    
    def generate_report(self, document: PolicyDocument, compliance_report: ComplianceReport, 
                       ai_analysis: Optional[Dict[str, Any]] = None, 
                       output_path: Optional[str] = None) -> str:
        """Generate a comprehensive compliance report"""
        
        report_data = {
            "document_info": {
                "title": document.title,
                "file_path": document.file_path,
                "word_count": document.metadata.get('word_count', 0),
                "sections": len(document.sections),
                "checked_at": compliance_report.checked_at.isoformat()
            },
            "compliance_results": {
                "score": compliance_report.compliance_score,
                "total_rules_checked": compliance_report.total_rules_checked,
                "violations_summary": compliance_report.summary,
                "violations": [
                    {
                        "rule_id": v.rule_id,
                        "rule_name": v.rule_name,
                        "level": v.level.value,
                        "description": v.description,
                        "location": v.location,
                        "suggestion": v.suggestion
                    }
                    for v in compliance_report.violations
                ]
            }
        }
        
        if ai_analysis:
            report_data["ai_analysis"] = ai_analysis
        
        # Convert to JSON string
        report_json = json.dumps(report_data, indent=2, default=str)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_json)
            print(f"✓ Report saved to: {output_path}")
        
        return report_json
    
    def list_available_rules(self) -> List[Dict[str, str]]:
        """List all available compliance rules"""
        rules_info = []
        for rule in self.compliance_engine.rules:
            rules_info.append({
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "level": rule.level.value,
                "type": rule.rule_type,
                "category": rule.metadata.get('category', 'general')
            })
        return rules_info
    
    def get_rule_categories(self) -> Dict[str, List[str]]:
        """Get rules organized by category"""
        categories = {}
        for rule in self.compliance_engine.rules:
            category = rule.metadata.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(rule.id)
        return categories


async def main():
    """Example usage of the Policy Compliance Checker"""
    
    # Initialize the checker
    checker = PolicyComplianceChecker(
        azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    await checker.initialize()
    
    # Load compliance rules
    rules_path = "assets/rule_templates/legal_compliance_rules.json"
    if os.path.exists(rules_path):
        checker.load_compliance_rules(rules_path)
    
    # Parse a document
    document_path = "assets/test_documents/employee_code_of_conduct.md"
    if os.path.exists(document_path):
        document = checker.parse_document(document_path)
        
        # Check compliance
        compliance_report = checker.check_compliance(document)
        
        # AI analysis (if enabled)
        if checker.ai_analysis_enabled:
            ai_analysis = await checker.ai_analyze_document(document)
            ai_suggestions = await checker.ai_suggest_improvements(document)
        else:
            ai_analysis = None
            ai_suggestions = None
        
        # Generate report
        report = checker.generate_report(
            document, compliance_report, ai_analysis, 
            "compliance_report.json"
        )
        
        print("\n📄 Report generated successfully!")


if __name__ == "__main__":
    asyncio.run(main())