# IAM Access Recertification Report

**Generated:** 2026-09-24T13:55:15.565286+00:00
**Stale access threshold:** 90 days of inactivity
**Source data:** `reports/access-review-20260924-135515.json`

---

## IAM Users

### sanika-admin

- Account age: 7 days
- Console access: Yes
- MFA enabled: **NO — FINDING**
- Attached policies: IAMUserChangePassword, security-lab-terraform-scoped-policy

  **FINDING:** User has console (password-based) access but no MFA device registered. This is a control gap against ISO 27001 A.8.5 (Secure Authentication) and represents elevated account-takeover risk. **Recommended action:** enforce MFA enrollment before next login, or restrict to programmatic (access-key-only) access if console login is not required.

  - Access key `AKIA3FLD4MWYA5UPBM3E` (Active)

## IAM Roles

| Role | Type | Age (days) | Last Used | Finding |
|---|---|---|---|---|
| AWSServiceRoleForAmazonGuardDuty | AWS service-linked | 2 | Never (or not tracked) | N/A (AWS-managed) |
| AWSServiceRoleForAmazonGuardDutyMalwareProtection | AWS service-linked | 2 | Never (or not tracked) | N/A (AWS-managed) |
| AWSServiceRoleForResourceExplorer | AWS service-linked | 7 | Never (or not tracked) | N/A (AWS-managed) |
| AWSServiceRoleForSupport | AWS service-linked | 925 | Never (or not tracked) | N/A (AWS-managed) |
| AWSServiceRoleForTrustedAdvisor | AWS service-linked | 925 | Never (or not tracked) | N/A (AWS-managed) |
| security-lab-config-role | Customer-managed | 2 | Never (or not tracked) | **Stale — review for removal** |
| security-lab-lambda-response-role | Customer-managed | 2 | Never (or not tracked) | **Stale — review for removal** |
| security-lab-ssm-instance-role | Customer-managed | 2 | Never (or not tracked) | **Stale — review for removal** |

---

## Summary: 4 finding(s) requiring review

This report should be reviewed by the account owner or designated approver, with each finding either remediated, accepted as a documented risk, or scheduled for follow-up by a specific date.