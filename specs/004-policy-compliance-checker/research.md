# Research: Policy Compliance Checker

**Feature**: 004-policy-compliance-checker
**Date**: 2026-01-12

## Research Tasks Completed

### 1. Document Parsing Libraries

**Decision**: pypdf 6.1.1+ for PDF, python-docx for DOCX, markdown-it-py for Markdown

**Rationale**:
- pypdf is the modern successor to PyPDF2 with better text extraction
- python-docx provides full DOCX support with paragraph/section preservation
- markdown-it-py is fast and CommonMark compliant
- All libraries are well-maintained and actively developed

**Alternatives Considered**:
- PyMuPDF: Better OCR support but heavier dependency
- pdfplumber: Good table extraction but slower for text-only
- PyPDF2: Deprecated, replaced by pypdf

### 2. AI Orchestration Framework

**Decision**: Microsoft Semantic Kernel 1.37.0

**Rationale**:
- Consistent with other hackathon projects (002, 003)
- Native plugin architecture for compliance analysis
- Built-in Azure OpenAI integration
- Supports prompt chaining for multi-step analysis

**Alternatives Considered**:
- LangChain: More complex, heavier dependency footprint
- Direct OpenAI API: Less structured, harder to extend
- Guidance: Less mature plugin system

### 3. Compliance Rule Engine Design

**Decision**: Pattern-based rules with regex support and AI-enhanced analysis

**Rationale**:
- Regex patterns provide fast, deterministic matching
- AI analysis catches semantic issues patterns miss
- Severity levels align with industry standards (Critical, High, Medium, Low)
- Category-based organization enables rule templates

**Algorithm**:
```python
class ComplianceRule:
    name: str
    description: str
    pattern: str  # Regex pattern
    severity: Severity  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # e.g., "data_protection", "hr_policy"

def evaluate_rule(rule: ComplianceRule, document: PolicyDocument) -> list[Violation]:
    matches = re.finditer(rule.pattern, document.content, re.IGNORECASE)
    violations = []
    for match in matches:
        violations.append(Violation(
            rule=rule,
            location=match.span(),
            context=match.group(),
            recommendation=generate_recommendation(rule)
        ))
    return violations
```

### 4. Report Generation

**Decision**: Structured JSON with optional HTML rendering

**Rationale**:
- JSON format enables programmatic consumption
- HTML rendering for human-readable reports
- Compliance score calculated as weighted sum of violations
- Recommendations generated per violation type

**Score Calculation**:
```python
severity_weights = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 5,
    Severity.LOW: 1
}

def calculate_score(violations: list[Violation], max_rules: int) -> float:
    penalty = sum(severity_weights[v.rule.severity] for v in violations)
    base_score = 100
    return max(0, base_score - penalty)
```

### 5. Rule Template Categories

**Decision**: 5 predefined template categories

**Rationale**:
- Covers most common compliance domains
- Extensible to organization-specific needs
- Each template contains 10-20 rules

**Templates**:
1. **Data Protection**: GDPR, CCPA, data retention, PII handling
2. **HR Policies**: Employment law, workplace safety, anti-discrimination
3. **IT Security**: Access control, password policies, incident response
4. **Legal Compliance**: Contract terms, liability, regulatory requirements
5. **Accessibility**: ADA compliance, inclusive language, accommodation

### 6. Web Framework

**Decision**: Flask 3.x with async support

**Rationale**:
- Consistent with hackathon projects (002, 003)
- Lightweight, minimal boilerplate
- Easy static file serving for potential web dashboard
- Blueprint pattern for modular API routes

**Alternatives Considered**:
- FastAPI: Better for pure API, overkill for demo
- Django: Too heavy for single-purpose tool

### 7. Data Validation

**Decision**: Pydantic 2.x with field validators

**Rationale**:
- Consistent with hackathon projects
- Native JSON serialization/deserialization
- Field validators for domain-specific rules
- Excellent type hints and IDE support

### 8. Testing Strategy

**Decision**: pytest 8.4.2+ with contract and integration tests

**Rationale**:
- Existing test suite with 59 tests to extend
- Contract tests verify API behavior
- Integration tests validate end-to-end workflows
- Unit tests for individual components

**Test Categories**:
- Setup tests (9): Environment validation
- Unit tests (24): Core component testing
- Integration tests (15): Multi-component workflows
- Plugin tests (11): Semantic Kernel plugin testing

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle large documents? | Stream processing with 10MB limit |
| What file formats to support? | PDF, DOCX, Markdown (text files) |
| How to calculate compliance score? | Weighted penalty system from 100 |
| How to generate recommendations? | Rule-based templates with AI enhancement |
| How to handle AI unavailability? | Pattern-only fallback mode |

## Dependencies Confirmed

```text
semantic-kernel>=1.37.0
pypdf>=6.1.1
python-docx>=1.0.0
markdown-it-py>=3.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
flask[async]>=3.0.0
python-dotenv>=1.0.0
pytest>=8.4.2
aiohttp>=3.9.0
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Azure OpenAI rate limits | Pattern-only fallback, caching |
| Large document processing | 10MB limit, streaming extraction |
| Complex PDF layouts | Focus on text content, flag complex layouts |
| Rule pattern errors | Regex validation on rule creation |
