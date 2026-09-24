# Debugging Notes

## False-positive stale-role finding: root cause and fix

**Symptom:** The first run of `access_review.py` flagged all three customer-managed IAM roles (`security-lab-config-role`, `security-lab-lambda-response-role`, `security-lab-ssm-instance-role`) as stale/never-used, despite these roles being actively used minutes earlier by AWS Config, Lambda, and SSM respectively in the connected `aws-cloud-security-baseline` project.

**Cross-validation:** Rather than trusting the tool's own output, the finding was checked against a second, independent data source: `aws iam get-role --role-name <role>` for two of the flagged roles, called directly via the AWS CLI. Both showed a populated, recent `RoleLastUsed.LastUsedDate` - directly contradicting the tool's "never used" finding.

**Root cause:** `iam:ListRoles` (the bulk API call the tool used to enumerate all roles) does not return the `RoleLastUsed` field at all - confirmed by printing the raw `list_roles()` response for a role known to be in active use, which had no `RoleLastUsed` key present. This field is only populated by `iam:GetRole`, a separate, per-role API call. This is a documented AWS API behaviour, not a bug in AWS or in this tool's logic - but using the wrong call for the data needed produced a real, meaningfully wrong finding (a role that IS in active use reported as a candidate for removal).

**Fix:** the tool now calls `get_role()` individually for each role during the review, rather than relying on the `RoleLastUsed` field from the bulk `list_roles()` response. Re-run and confirmed correct: all three actively-used roles now show accurate, recent last-used timestamps and no longer appear in the findings list.

**Why this matters for a governance tool specifically:** an access review tool that produces false "unused, recommend removal" findings is actively dangerous in a real environment - acting on it would mean deleting IAM roles that production infrastructure (Config, Lambda, SSM) depends on. Cross-validating a tool's output against an independent source before trusting its findings, especially for anything a reviewer might act on, is standard practice this project follows throughout.
