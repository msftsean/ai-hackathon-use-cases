# Data Model: Policy Compliance Checker

**Feature**: 004-policy-compliance-checker
**Date**: 2026-01-12

## Entity Overview

```
┌─────────────────────┐     analyzes    ┌─────────────────────────┐
│   PolicyDocument    │────────────────▶│    ComplianceReport     │
└─────────────────────┘                 └─────────────────────────┘
         │                                        │
         │ contains                               │ contains
         ▼                                        ▼
┌─────────────────────┐                ┌─────────────────────────┐
│   DocumentSection   │                │   ComplianceViolation   │
└─────────────────────┘                └─────────────────────────┘
                                                  │
┌─────────────────────┐     evaluates             │ references
│   ComplianceRule    │◀──────────────────────────┘
└─────────────────────┘
         │
         │ belongs to
         ▼
┌─────────────────────┐
│    RuleTemplate     │
└─────────────────────┘
```

## Enumerations

### Severity

| Value | Level | Weight | Description |
|-------|-------|--------|-------------|
| `CRITICAL` | 4 | 25 | Must be addressed immediately, legal/regulatory risk |
| `HIGH` | 3 | 15 | Significant issue, should be addressed promptly |
| `MEDIUM` | 2 | 5 | Moderate concern, should be reviewed |
| `LOW` | 1 | 1 | Minor issue, best practice recommendation |

### DocumentFormat

| Value | Description |
|-------|-------------|
| `PDF` | Portable Document Format files |
| `DOCX` | Microsoft Word documents |
| `MARKDOWN` | Markdown text files |
| `TEXT` | Plain text files |

### RuleCategory

| Value | Description |
|-------|-------------|
| `DATA_PROTECTION` | GDPR, CCPA, privacy rules |
| `HR_POLICY` | Employment, workplace rules |
| `IT_SECURITY` | Access control, security policies |
| `LEGAL_COMPLIANCE` | Regulatory, contractual rules |
| `ACCESSIBILITY` | ADA, inclusive design rules |
| `CUSTOM` | Organization-specific rules |

### AnalysisStatus

| Value | Description |
|-------|-------------|
| `PENDING` | Document uploaded, not analyzed |
| `PROCESSING` | Analysis in progress |
| `COMPLETED` | Analysis finished successfully |
| `FAILED` | Analysis failed with error |

## Core Entities

### PolicyDocument

Represents an uploaded policy document.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `document_id` | string | Yes | UUID format | Unique identifier |
| `filename` | string | Yes | Non-empty | Original filename |
| `format` | DocumentFormat | Yes | Valid enum | File format |
| `content` | string | Yes | Non-empty | Extracted text content |
| `sections` | list[DocumentSection] | No | - | Parsed document sections |
| `metadata` | dict[str, str] | No | - | Document properties |
| `file_size_bytes` | int | Yes | > 0, <= 10MB | File size |
| `page_count` | int | No | >= 0 | Number of pages (PDF) |
| `upload_timestamp` | datetime | Auto | - | Upload time |
| `status` | AnalysisStatus | Yes | Valid enum | Processing status |

**Validation Rules**:
- `file_size_bytes` must be positive and <= 10,485,760 (10MB)
- `document_id` must be unique within system
- `content` must have at least 10 characters

### DocumentSection

A section within a policy document.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `section_id` | string | Yes | Unique within document |
| `title` | string | No | Section heading if present |
| `content` | string | Yes | Section text content |
| `level` | int | Yes | Heading level (1-6) |
| `start_position` | int | Yes | Character offset in document |
| `end_position` | int | Yes | End character offset |

### ComplianceRule

A rule for compliance checking.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `rule_id` | string | Yes | UUID format | Unique identifier |
| `name` | string | Yes | 3-100 chars | Rule name |
| `description` | string | Yes | Non-empty | What rule checks |
| `pattern` | string | Yes | Valid regex | Regex pattern |
| `severity` | Severity | Yes | Valid enum | Violation severity |
| `category` | RuleCategory | Yes | Valid enum | Rule category |
| `recommendation_template` | string | No | - | Recommendation text |
| `is_active` | bool | Yes | - | Whether rule is enabled |
| `created_at` | datetime | Auto | - | Creation timestamp |
| `updated_at` | datetime | Auto | - | Last modification |

**Validation Rules**:
- `pattern` must be a valid Python regex
- `name` must be unique within category
- `severity` determines violation weight

### ComplianceViolation

A specific violation found during analysis.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `violation_id` | string | Yes | Unique identifier |
| `rule` | ComplianceRule | Yes | Rule that was violated |
| `document_id` | string | Yes | Source document |
| `location_start` | int | Yes | Character offset start |
| `location_end` | int | Yes | Character offset end |
| `matched_text` | string | Yes | Text that matched pattern |
| `context` | string | Yes | Surrounding text (100 chars) |
| `section` | DocumentSection | No | Section if identifiable |
| `recommendation` | string | Yes | Specific fix recommendation |
| `detected_at` | datetime | Auto | Detection timestamp |

### ComplianceReport

Analysis results for a document.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_id` | string | Yes | Unique identifier |
| `document` | PolicyDocument | Yes | Analyzed document |
| `violations` | list[ComplianceViolation] | Yes | All violations found |
| `rules_applied` | list[ComplianceRule] | Yes | Rules used in analysis |
| `compliance_score` | float | Yes | Score 0-100 |
| `summary` | ReportSummary | Yes | Statistical summary |
| `ai_insights` | list[str] | No | AI-generated observations |
| `generated_at` | datetime | Auto | Report generation time |
| `analysis_duration_ms` | int | Yes | Processing time |

### ReportSummary

Statistical summary of analysis results.

| Field | Type | Description |
|-------|------|-------------|
| `total_rules_checked` | int | Number of rules applied |
| `total_violations` | int | Total violations found |
| `critical_count` | int | CRITICAL severity count |
| `high_count` | int | HIGH severity count |
| `medium_count` | int | MEDIUM severity count |
| `low_count` | int | LOW severity count |
| `categories_affected` | list[RuleCategory] | Categories with violations |
| `pass_rate` | float | Percentage of rules passed |

### RuleTemplate

A predefined set of compliance rules.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_id` | string | Yes | Unique identifier |
| `name` | string | Yes | Template name |
| `description` | string | Yes | What template covers |
| `category` | RuleCategory | Yes | Primary category |
| `rules` | list[ComplianceRule] | Yes | Rules in template |
| `version` | string | Yes | Template version |
| `is_builtin` | bool | Yes | System-provided vs custom |
| `created_at` | datetime | Auto | Creation timestamp |

**Default Templates**:
- Data Protection Template (15 rules)
- HR Policy Template (12 rules)
- IT Security Template (18 rules)
- Legal Compliance Template (10 rules)
- Accessibility Template (8 rules)

### ComparisonResult

Result of comparing two policy versions.

| Field | Type | Description |
|-------|------|-------------|
| `comparison_id` | string | Unique identifier |
| `document_a` | PolicyDocument | First document |
| `document_b` | PolicyDocument | Second document |
| `additions` | list[TextChange] | New text in document_b |
| `removals` | list[TextChange] | Removed from document_a |
| `modifications` | list[TextChange] | Changed sections |
| `compliance_impact` | list[str] | Potential compliance effects |
| `compared_at` | datetime | Comparison timestamp |

### TextChange

A specific text change between versions.

| Field | Type | Description |
|-------|------|-------------|
| `change_type` | string | "addition", "removal", "modification" |
| `section` | DocumentSection | Affected section |
| `old_text` | string | Original text (if applicable) |
| `new_text` | string | New text (if applicable) |
| `position` | int | Character position |

## State Transitions

### Document Lifecycle

```
Uploaded → PENDING → PROCESSING → COMPLETED
                         ↓
                      FAILED
```

### Analysis Workflow

```
Document Upload → Parse Sections → Apply Rules → Generate Violations
                                                       ↓
                                              Calculate Score → Generate Report
```

## Indexes and Queries

### Primary Queries

1. **Get document by ID**: `document_id` (exact match)
2. **Get report by document**: `report.document_id` (exact match)
3. **Search rules by category**: `rule.category` (enum filter)
4. **Filter violations by severity**: `violation.rule.severity` (enum filter)
5. **List templates**: `template.is_builtin` (boolean filter)

### Secondary Indexes

- `ComplianceRule.category` for filtering
- `ComplianceRule.severity` for filtering
- `ComplianceViolation.rule_id` for grouping
- `PolicyDocument.upload_timestamp` for sorting
