# IAM Access Governance & Recertification Tool - Project Report

Author: Sanika Mahamulkar, MSc Cybersecurity, University of Bristol
Repository: https://github.com/SanikaMahamulkar/iam-access-governance
Date: September 2026

## Executive Summary

This project builds an automated IAM access review tool: it enumerates users and roles in a live AWS account, checks last-activity and MFA status, flags stale or unused access, and produces an audit-ready recertification report with findings mapped to ISO 27001 controls. It extends aws-cloud-security-baseline, reviewing the same account this project's infrastructure work built - demonstrating not just the ability to design least-privilege access, but the ongoing governance discipline of periodically proving that access remains correct.

The tool surfaced one genuine finding on its first real run (a console-access IAM user with no MFA enrolled) and, during development, surfaced and led to the correction of a real bug in the tool itself - a false "stale access" finding on three actively-used IAM roles, caused by a documented AWS API behaviour (`iam:ListRoles` not returning the `RoleLastUsed` field that only `iam:GetRole` provides). This was caught by deliberately cross-validating the tool's own output against a second, independent data source before trusting it - the same validation discipline applied throughout this project series.

## Objectives

1. Build a working IAM access review tool against a real AWS account, not synthetic data.
2. Detect stale/unused access keys, unused IAM roles, and missing MFA on console-access users.
3. Produce an audit-ready recertification report, not just raw findings - the actual artifact a GRC analyst would hand to an approver.
4. Map every automated check to a specific ISO 27001 control.
5. Validate the tool's findings against independent evidence before trusting them.
6. Automate the review on a schedule via CI/CD.

## Methodology

The tool was run against the live AWS account from aws-cloud-security-baseline, which already had real, mixed IAM history: a single admin user, several AWS service-linked roles, and three customer-managed roles genuinely in active use (Config, Lambda, SSM). This real, imperfect dataset was deliberately preferred over a synthetic one, since a review tool's value is entirely in how well it handles real-world noise and edge cases.

Building the tool immediately required extending the existing least-privilege IAM policy from the infrastructure project: `iam:ListUsers` and `iam:ListRoles` were not present, since the original policy was scoped for infrastructure deployment, not access auditing - a legitimate distinction, but one this project's first real step had to resolve. Applying that policy update itself hit a genuine bootstrap problem: updating a policy that manages its own IAM permissions requires an IAM action (`iam:ListPolicyVersions`) that did not yet exist in the policy being updated. This was resolved by temporarily attaching AWS's managed `IAMReadOnlyAccess` policy to complete the update, then detaching it once the scoped policy was self-sufficient - documented as a real, reusable pattern for anyone self-managing their own least-privilege policy.

## Findings

**Genuine finding, left in place as evidence:** the `sanika-admin` IAM user has console (password-based) access with no MFA device registered - a real control gap against ISO 27001 A.8.5, surfaced by the tool's first real run against the live account.

**Bug found and fixed during development:** the tool's first run flagged all three customer-managed IAM roles as stale/never-used, despite two of them having been used minutes earlier. This was checked against `aws iam get-role`, called directly via CLI, which showed accurate recent-use data - directly contradicting the tool's own finding. Root cause: `iam:ListRoles`, the bulk API call used to enumerate roles, does not return the `RoleLastUsed` field at all; only the per-role `iam:GetRole` call does. This was confirmed by printing the raw API response and observing the field was absent entirely, not merely empty. Fixed by calling `get_role()` individually per role during the review. Re-run and confirmed correct. Full detail is in debugging-notes.md.

This distinction matters specifically because this is a governance tool: a false "unused, recommend removal" finding, acted on without question, would mean deleting IAM roles that production infrastructure actually depends on. Cross-validating any finding a reviewer might act on, rather than trusting a tool's first output, is treated as a non-negotiable practice throughout this project.

## Control Mapping

Full detail in control-mapping.md. In summary: MFA enforcement maps to ISO 27001 A.8.5; stale access key and role detection map to A.5.18 and A.8.2; attached-policy visibility supports the least-privilege review process under A.5.15/A.8.2. The tool reports findings only - it does not remediate automatically, since removing access or enforcing MFA is a decision for an account owner or approver, not something a review script should do unattended.

## CI/CD

A scheduled GitHub Actions workflow runs the review monthly (and on manual dispatch), producing both the JSON evidence and the Markdown recertification report as build artifacts. Running this in CI requires AWS credentials configured as GitHub Secrets - deliberately not activated as part of this project's development, since doing so responsibly requires provisioning a dedicated, minimally-scoped credential for CI use rather than reusing the broader `sanika-admin` credentials, which is a separate decision documented but not rushed into.

## Conclusion

This project delivers a working access governance tool validated against a real AWS account with real findings - including one the tool got wrong on its first attempt, caught, root-caused to a specific AWS API behaviour, and fixed. It demonstrates the governance side of access management directly: not just designing least-privilege access (covered in aws-cloud-security-baseline), but the recurring discipline of proving that access remains correct over time, producing evidence an auditor or approver could actually act on.

## Skills Demonstrated

- IAM governance: access recertification, stale-access detection, MFA compliance checking
- Python scripting with boto3 (AWS SDK)
- ISO 27001 control mapping for access management controls
- Cross-validating tool output against independent evidence before trusting findings
- Root-causing a real bug to a specific, documented API behaviour rather than a guess
- IAM self-management bootstrap problem-solving
- CI/CD design for scheduled, credentialed automation (with a documented, deliberate decision on when to activate real credentials)
- Audit-ready report generation for non-technical approvers
