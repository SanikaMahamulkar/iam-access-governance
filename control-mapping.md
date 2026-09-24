# Control Mapping

This document maps each automated check in `access_review.py` to the compliance control it supports.

| Check | Control | Framework Reference |
|---|---|---|
| MFA enrollment check on console-access users | Secure authentication for privileged/interactive access | ISO 27001:2022 A.8.5 |
| Stale access key detection (>90 days unused) | Periodic access review and revocation of unused credentials | ISO 27001:2022 A.5.18, A.8.2 |
| Never-used access key detection | Provisioning review - unused credentials should not remain active | ISO 27001:2022 A.5.18 |
| Stale IAM role detection (customer-managed, >90 days unused) | Periodic review of granted access and roles | ISO 27001:2022 A.5.18, A.8.2 |
| Attached policy enumeration per user | Visibility into granted permissions, supporting least-privilege review | ISO 27001:2022 A.5.15, A.8.2 |

## Review Cadence

This tool is designed to be run periodically (recommended: monthly for a small environment, quarterly minimum) as part of a standing access recertification process. Each run produces two artifacts:

1. A raw JSON review (`reports/access-review-*.json`) - the underlying evidence.
2. A human-readable recertification report (`reports/recertification-report-*.md`) - the artifact intended for an approver's sign-off.

## Scope and Limitations

- This tool reviews IAM users, roles, access keys, MFA status, and attached policies. It does not currently review resource-based policies (e.g. S3 bucket policies), cross-account trust relationships, or federated/SSO access - these would need separate tooling or an extension of this one.
- The `90`-day stale threshold is a starting default, not a regulatory requirement; a real deployment should set this based on the organisation's own access review policy.
- This tool reports findings; it does not remediate them automatically. Deliberately so - removing access or enforcing MFA is a decision for the account owner or designated approver, not something a review tool should do unattended.
