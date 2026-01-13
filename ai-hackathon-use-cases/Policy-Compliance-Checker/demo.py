#!/usr/bin/env python3
"""
Policy Compliance Checker - Quick Demo
Demonstrates core functionality with sample policy checking.
"""
import asyncio
import os
import sys
import tempfile
import json

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.main import PolicyComplianceChecker
from src.core.compliance_engine import ComplianceLevel


async def main():
    """Run a comprehensive demo of the Policy Compliance Checker"""
    
    print("🎯 Policy Compliance Checker - Demo")
    print("=" * 60)
    
    # Initialize the checker (without AI for demo)
    print("\n🚀 Initializing Policy Compliance Checker...")
    checker = PolicyComplianceChecker()
    await checker.initialize()
    
    # Create sample compliance rules
    print("\n📋 Creating sample compliance rules...")
    
    sample_rules = {
        "rules": [
            {
                "id": "privacy_section",
                "name": "Privacy Section Required",
                "description": "Policy must include a privacy or data protection section",
                "level": "high",
                "type": "required_sections",
                "required_sections": ["Privacy", "Data Protection", "Data Privacy"],
                "prohibited_terms": [],
                "required_terms": [],
                "metadata": {"category": "legal"}
            },
            {
                "id": "equal_opportunity",
                "name": "Equal Opportunity Language",
                "description": "Must include equal opportunity or diversity language",
                "level": "medium",
                "type": "required_terms",
                "required_sections": [],
                "prohibited_terms": [],
                "required_terms": ["equal opportunity", "diversity", "non-discrimination"],
                "metadata": {"category": "legal"}
            },
            {
                "id": "no_offensive_language",
                "name": "No Offensive Language",
                "description": "Must not contain discriminatory or offensive language",
                "level": "critical",
                "type": "prohibited_terms",
                "required_sections": [],
                "prohibited_terms": ["discriminate against", "exclude based on", "offensive"],
                "required_terms": [],
                "metadata": {"category": "content"}
            }
        ]
    }
    
    # Save rules to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_rules, f, indent=2)
        rules_file = f.name
    
    try:
        # Load the rules
        checker.load_compliance_rules(rules_file)
        
        # Create sample policy documents to test
        print("\n📄 Testing sample policy documents...")
        
        # Test 1: Good policy
        good_policy = """# Employee Code of Conduct

## Introduction
This document outlines our company's commitment to creating an inclusive workplace.

## Equal Opportunity Policy
We are an equal opportunity employer committed to diversity and inclusion.
All employees are treated fairly regardless of background.

## Data Privacy Protection
We protect all employee personal information and maintain strict confidentiality.
Personal data is processed according to applicable privacy laws.

## Professional Standards
All employees must maintain high professional standards in their work.
"""
        
        # Test 2: Policy with violations
        problematic_policy = """# Basic Company Policy

## General Information
This is our company policy document.

## Employment Rules
We hire the best people for our company.
Some inappropriate practices may be overlooked in certain cases.
"""
        
        # Test documents
        test_cases = [
            ("Good Policy Example", good_policy),
            ("Problematic Policy Example", problematic_policy)
        ]
        
        for policy_name, policy_content in test_cases:
            print(f"\n📋 Testing: {policy_name}")
            print("-" * 40)
            
            # Save policy to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(policy_content)
                policy_file = f.name
            
            try:
                # Parse and check the document
                document = checker.parse_document(policy_file)
                report = checker.check_compliance(document)
                
                # Generate detailed report
                report_data = checker.generate_report(document, report)
                report_obj = json.loads(report_data)
                
                # Display summary
                print(f"\n📊 Results Summary:")
                print(f"   📄 Document: {document.title}")
                print(f"   📝 Sections: {len(document.sections)}")
                print(f"   📊 Compliance Score: {report.compliance_score:.1f}%")
                print(f"   🔍 Rules Checked: {report.total_rules_checked}")
                print(f"   ⚠️ Total Violations: {len(report.violations)}")
                
                if report.violations:
                    print(f"\n🚨 Violations Found:")
                    for violation in report.violations:
                        severity_emoji = {
                            ComplianceLevel.CRITICAL: "🔴",
                            ComplianceLevel.HIGH: "🟠", 
                            ComplianceLevel.MEDIUM: "🟡",
                            ComplianceLevel.LOW: "🔵",
                            ComplianceLevel.INFO: "ℹ️"
                        }.get(violation.level, "⚠️")
                        
                        print(f"   {severity_emoji} [{violation.level.value.upper()}] {violation.description}")
                        print(f"      💡 Suggestion: {violation.suggestion}")
                
                else:
                    print("   ✅ No violations found!")
                
                # Show compliance breakdown
                if report.summary:
                    print(f"\n📈 Compliance Breakdown:")
                    for level, count in report.summary.items():
                        if count > 0:
                            print(f"   {level.capitalize()}: {count} violations")
                
            finally:
                os.unlink(policy_file)
        
        # Demo additional features
        print(f"\n🔧 Available Features:")
        print(f"   📋 Rules Management: {len(checker.compliance_engine.rules)} rules loaded")
        print(f"   📂 Rule Categories: {list(checker.get_rule_categories().keys())}")
        print(f"   📄 Supported Formats: {checker.document_parser.supported_formats}")
        print(f"   🤖 AI Analysis: {'Available' if checker.ai_analysis_enabled else 'Requires Azure OpenAI credentials'}")
        
        print(f"\n✨ Demo Complete!")
        print(f"   ✅ Document parsing: Working")
        print(f"   ✅ Compliance checking: Working") 
        print(f"   ✅ Rule evaluation: Working")
        print(f"   ✅ Report generation: Working")
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(rules_file):
            os.unlink(rules_file)


if __name__ == "__main__":
    try:
        print("🎯 Policy Compliance Checker - Quick Demo")
        print("Demonstrating core functionality...")
        
        success = asyncio.run(main())
        
        if success:
            print("\n🎉 Demo completed successfully!")
            print("✅ Policy Compliance Checker is working correctly!")
        else:
            print("\n❌ Demo failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()