"""
Policy Compliance Checker - Compliance Rules Engine
Handles rule evaluation and compliance checking logic.
"""
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ComplianceLevel(Enum):
    """Compliance severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ComplianceRule:
    """Represents a compliance rule"""
    id: str
    name: str
    description: str
    level: ComplianceLevel
    pattern: str
    rule_type: str
    required_sections: List[str]
    prohibited_terms: List[str]
    required_terms: List[str]
    metadata: Dict[str, Any]


@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""
    rule_id: str
    rule_name: str
    level: ComplianceLevel
    description: str
    location: str
    context: str
    suggestion: str
    line_number: Optional[int] = None


@dataclass
class ComplianceReport:
    """Compliance check report"""
    document_title: str
    document_path: str
    total_rules_checked: int
    violations: List[ComplianceViolation]
    compliance_score: float
    checked_at: datetime
    summary: Dict[str, int]


class ComplianceRulesEngine:
    """Handles compliance rule evaluation"""
    
    def __init__(self):
        self.rules: List[ComplianceRule] = []
        self.rule_categories = {
            "legal": "Legal compliance requirements",
            "consistency": "Document consistency checks",
            "security": "Security policy requirements",
            "accessibility": "Accessibility compliance",
            "data_protection": "Data protection requirements"
        }
    
    def load_rules_from_file(self, rules_file_path: str) -> None:
        """Load compliance rules from JSON file"""
        try:
            with open(rules_file_path, 'r', encoding='utf-8') as file:
                rules_data = json.load(file)
                self.rules = []
                
                for rule_data in rules_data.get('rules', []):
                    rule = ComplianceRule(
                        id=rule_data['id'],
                        name=rule_data['name'],
                        description=rule_data['description'],
                        level=ComplianceLevel(rule_data['level']),
                        pattern=rule_data.get('pattern', ''),
                        rule_type=rule_data.get('type', 'text'),
                        required_sections=rule_data.get('required_sections', []),
                        prohibited_terms=rule_data.get('prohibited_terms', []),
                        required_terms=rule_data.get('required_terms', []),
                        metadata=rule_data.get('metadata', {})
                    )
                    self.rules.append(rule)
        except Exception as e:
            raise ValueError(f"Error loading rules from {rules_file_path}: {str(e)}")
    
    def add_rule(self, rule: ComplianceRule) -> None:
        """Add a compliance rule"""
        self.rules.append(rule)
    
    def check_compliance(self, document, selected_rules: Optional[List[str]] = None) -> ComplianceReport:
        """Check document compliance against rules"""
        violations = []
        rules_to_check = self.rules
        
        if selected_rules:
            rules_to_check = [rule for rule in self.rules if rule.id in selected_rules]
        
        for rule in rules_to_check:
            rule_violations = self._evaluate_rule(document, rule)
            violations.extend(rule_violations)
        
        # Calculate compliance score
        total_possible_violations = len(rules_to_check)
        if total_possible_violations == 0:
            compliance_score = 100.0
        else:
            # Weight violations by severity
            weighted_violations = sum(
                self._get_violation_weight(v.level) for v in violations
            )
            max_possible_weight = sum(
                self._get_violation_weight(rule.level) for rule in rules_to_check
            )
            compliance_score = max(0, 100 - (weighted_violations / max_possible_weight * 100))
        
        # Create summary
        summary = {
            "critical": len([v for v in violations if v.level == ComplianceLevel.CRITICAL]),
            "high": len([v for v in violations if v.level == ComplianceLevel.HIGH]),
            "medium": len([v for v in violations if v.level == ComplianceLevel.MEDIUM]),
            "low": len([v for v in violations if v.level == ComplianceLevel.LOW]),
            "info": len([v for v in violations if v.level == ComplianceLevel.INFO])
        }
        
        return ComplianceReport(
            document_title=document.title,
            document_path=document.file_path,
            total_rules_checked=len(rules_to_check),
            violations=violations,
            compliance_score=compliance_score,
            checked_at=datetime.now(),
            summary=summary
        )
    
    def _evaluate_rule(self, document, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Evaluate a single rule against a document"""
        violations = []
        
        if rule.rule_type == "required_sections":
            violations.extend(self._check_required_sections(document, rule))
        elif rule.rule_type == "prohibited_terms":
            violations.extend(self._check_prohibited_terms(document, rule))
        elif rule.rule_type == "required_terms":
            violations.extend(self._check_required_terms(document, rule))
        elif rule.rule_type == "pattern":
            violations.extend(self._check_pattern(document, rule))
        elif rule.rule_type == "consistency":
            violations.extend(self._check_consistency(document, rule))
        
        return violations
    
    def _check_required_sections(self, document, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check if required sections are present"""
        violations = []
        section_titles = [section["title"].lower() for section in document.sections]
        
        for required_section in rule.required_sections:
            found = any(required_section.lower() in title for title in section_titles)
            if not found:
                violations.append(ComplianceViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    level=rule.level,
                    description=f"Missing required section: {required_section}",
                    location="Document structure",
                    context=f"Available sections: {', '.join([s['title'] for s in document.sections[:3]])}...",
                    suggestion=f"Add a section titled '{required_section}' or similar"
                ))
        
        return violations
    
    def _check_prohibited_terms(self, document, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check for prohibited terms"""
        violations = []
        content_lower = document.content.lower()
        
        for term in rule.prohibited_terms:
            if term.lower() in content_lower:
                # Find context around the term
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                matches = list(pattern.finditer(document.content))
                
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(document.content), match.end() + 50)
                    context = document.content[start:end].replace('\n', ' ')
                    
                    violations.append(ComplianceViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        level=rule.level,
                        description=f"Prohibited term found: {term}",
                        location=f"Position {match.start()}",
                        context=f"...{context}...",
                        suggestion=rule.metadata.get('suggestion', f"Remove or replace '{term}'")
                    ))
        
        return violations
    
    def _check_required_terms(self, document, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check for required terms"""
        violations = []
        content_lower = document.content.lower()
        
        for term in rule.required_terms:
            if term.lower() not in content_lower:
                violations.append(ComplianceViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    level=rule.level,
                    description=f"Required term missing: {term}",
                    location="Document content",
                    context="Term not found in document",
                    suggestion=f"Include the term '{term}' in appropriate context"
                ))
        
        return violations
    
    def _check_pattern(self, document, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check for regex pattern matches"""
        violations = []
        
        try:
            pattern = re.compile(rule.pattern, re.IGNORECASE | re.MULTILINE)
            matches = list(pattern.finditer(document.content))
            
            if rule.metadata.get('should_match', True):
                # Pattern should be found
                if not matches:
                    violations.append(ComplianceViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        level=rule.level,
                        description=f"Required pattern not found: {rule.pattern}",
                        location="Document content",
                        context="Pattern not matched",
                        suggestion=rule.metadata.get('suggestion', 'Add content matching the required pattern')
                    ))
            else:
                # Pattern should NOT be found
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(document.content), match.end() + 50)
                    context = document.content[start:end].replace('\n', ' ')
                    
                    violations.append(ComplianceViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        level=rule.level,
                        description=f"Prohibited pattern found: {rule.pattern}",
                        location=f"Position {match.start()}",
                        context=f"...{context}...",
                        suggestion=rule.metadata.get('suggestion', 'Remove or modify the matching content')
                    ))
        except re.error as e:
            # Invalid regex pattern
            violations.append(ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                level=ComplianceLevel.INFO,
                description=f"Invalid regex pattern: {str(e)}",
                location="Rule configuration",
                context=rule.pattern,
                suggestion="Fix the regex pattern in the rule definition"
            ))
        
        return violations
    
    def _check_consistency(self, document, rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check document consistency rules"""
        violations = []
        
        # Example: Check for consistent terminology
        inconsistencies = rule.metadata.get('inconsistency_patterns', [])
        for inconsistency in inconsistencies:
            terms = inconsistency.get('terms', [])
            if len(terms) > 1:
                found_terms = []
                for term in terms:
                    if term.lower() in document.content.lower():
                        found_terms.append(term)
                
                if len(found_terms) > 1:
                    violations.append(ComplianceViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        level=rule.level,
                        description=f"Inconsistent terminology: {', '.join(found_terms)}",
                        location="Document content",
                        context=f"Multiple variants found: {found_terms}",
                        suggestion=f"Use consistent terminology. Choose one: {terms[0]}"
                    ))
        
        return violations
    
    def _get_violation_weight(self, level: ComplianceLevel) -> float:
        """Get weight for violation level"""
        weights = {
            ComplianceLevel.CRITICAL: 10.0,
            ComplianceLevel.HIGH: 5.0,
            ComplianceLevel.MEDIUM: 3.0,
            ComplianceLevel.LOW: 1.0,
            ComplianceLevel.INFO: 0.1
        }
        return weights.get(level, 1.0)
    
    def get_rules_by_category(self, category: str) -> List[ComplianceRule]:
        """Get rules filtered by category"""
        return [rule for rule in self.rules if rule.metadata.get('category', '') == category]
    
    def get_rule_by_id(self, rule_id: str) -> Optional[ComplianceRule]:
        """Get rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None