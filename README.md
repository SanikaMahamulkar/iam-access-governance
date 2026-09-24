# IAM Access Governance & Recertification Tool

Automated IAM access review tooling: detects stale/unused access, missing MFA, and never-used credentials, and produces audit-ready recertification reports with findings mapped to ISO 27001 controls.

This project extends [aws-cloud-security-baseline](https://github.com/SanikaMahamulkar/aws-cloud-security-baseline), reviewing the same live AWS account from a governance/audit perspective rather than an infrastructure-engineering one - the two together demonstrate both sides of access management: building least-privilege access, and then periodically proving it's still correct.

## Tech stack

- **Language:** Python 3, boto3 (AWS SDK)
- **Target:** AWS IAM (users, roles, access keys, MFA devices, policies)
- **CI/CD:** GitHub Actions (scheduled monthly run)
- **Output:** structured JSON (evidence) + human-readable Markdown (recertification report)

## Repository structure

- `scripts/access_review.py` - pulls IAM users/roles from AWS, checks last-activity and MFA status, outputs structured JSON findings
- `scripts/generate_recertification_report.py` - turns the JSON findings into an audit-ready Markdown report with control-mapped findings and recommended actions
- `reports/` - sample generated reports (real output from a real AWS account)
- `control-mapping.md` - maps each automated check to its ISO 27001 control
- `debugging-notes.md` - a real false-positive bug found via cross-validation, root-caused, and fixed
- `.github/workflows/access-review.yml` - scheduled CI workflow for monthly automated reviews (requires AWS credentials configured as GitHub Secrets to actually run)

## Progress log

- [x] Extended the existing least-privilege IAM policy (from aws-cloud-security-baseline) with read-only audit permissions needed for access review, working through a genuine self-management bootstrap issue
- [x] Built the core access review script: user/role enumeration, last-used activity, MFA status, access key staleness
- [x] Built the recertification report generator, producing audit-ready Markdown with control-mapped findings
- [x] Found, root-caused, and fixed a real false-positive bug (list_roles vs get_role API gap causing incorrect "stale" findings on actively-used roles)
- [x] Control mapping document (ISO 27001 A.5.18, A.8.2, A.8.5)
- [x] Scheduled CI workflow for automated monthly reviews
- [ ] Full project report

## Known findings from the sample run

The tool's most recent run against the live AWS account found 1 genuine finding: the `sanika-admin` IAM user has console (password) access without MFA enrolled - a real control gap, left in place intentionally as evidence the tool surfaces real issues rather than only synthetic ones.

## Author

Sanika Mahamulkar - MSc Cybersecurity, University of Bristol
