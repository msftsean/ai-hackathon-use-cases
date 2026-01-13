# Audit Log Retention Policy

## Purpose

This document outlines the retention policy for audit logs in the Inter-Agency Knowledge Hub, ensuring compliance with the LOADinG Act and NYS records retention requirements.

## Retention Period

All audit logs shall be retained for a minimum of **7 years** from the date of creation.

## Covered Data

The following audit data is subject to this retention policy:

1. **Search Queries**
   - Query text
   - User identifier
   - Timestamp
   - Agencies searched
   - Result count
   - Session information

2. **Document Access**
   - Document identifiers accessed
   - User identifier
   - Timestamp
   - Classification level of accessed documents
   - IP address

3. **Export Activities**
   - Export format
   - Documents included
   - User identifier
   - Timestamp

4. **Cross-Reference Views**
   - Source document
   - Related documents viewed
   - User identifier
   - Timestamp

5. **Review Flags**
   - Original query
   - Flag reason
   - Reviewer actions
   - Status changes
   - Timestamps

## Storage Requirements

- Audit logs must be stored in a secure, tamper-evident format
- Logs must be encrypted at rest
- Access to audit logs is restricted to authorized administrators
- Backup copies must be maintained in a geographically separate location

## Access Controls

- Only users with the `AllAgencies_Admin` role may access audit logs
- All access to audit logs is itself logged
- Export of audit data requires documented justification

## Disposal

After the 7-year retention period:
- Logs may be securely disposed of
- Disposal must be documented
- Cryptographic erasure is the preferred method

## Compliance

This policy complies with:
- NYS Arts and Cultural Affairs Law Section 57.05
- LOADinG Act requirements for AI transparency
- NIST SP 800-53 AU controls

## Review

This policy shall be reviewed annually and updated as needed to reflect changes in legal requirements or organizational needs.

---

*Last Updated: January 2024*
*Policy Owner: Office of Information Technology Services*
