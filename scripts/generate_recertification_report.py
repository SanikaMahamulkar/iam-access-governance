#!/usr/bin/env python3
"""
Generates a human-readable, audit-ready access recertification report
from the latest access_review.py JSON output.
"""

import json
import glob
import os
from datetime import datetime, timezone


def latest_report():
    files = sorted(glob.glob("reports/access-review-*.json"))
    if not files:
        raise SystemExit("No access review JSON found. Run access_review.py first.")
    return files[-1]


def main():
    path = latest_report()
    with open(path) as f:
        data = json.load(f)

    lines = []
    lines.append("# IAM Access Recertification Report")
    lines.append("")
    lines.append(f"**Generated:** {data['generated_at']}")
    lines.append(f"**Stale access threshold:** {data['stale_threshold_days']} days of inactivity")
    lines.append(f"**Source data:** `{path}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Users section
    lines.append("## IAM Users")
    lines.append("")
    findings_count = 0

    for user in data["users"]:
        lines.append(f"### {user['username']}")
        lines.append("")
        lines.append(f"- Account age: {user['account_age_days']} days")
        lines.append(f"- Console access: {'Yes' if user['has_console_access'] else 'No'}")
        lines.append(f"- MFA enabled: {'Yes' if user['mfa_enabled'] else '**NO — FINDING**'}")
        lines.append(f"- Attached policies: {', '.join(user['attached_policies']) if user['attached_policies'] else 'None'}")

        if not user["mfa_enabled"] and user["has_console_access"]:
            findings_count += 1
            lines.append("")
            lines.append("  **FINDING:** User has console (password-based) access but no MFA device registered. "
                          "This is a control gap against ISO 27001 A.8.5 (Secure Authentication) and represents "
                          "elevated account-takeover risk. **Recommended action:** enforce MFA enrollment before "
                          "next login, or restrict to programmatic (access-key-only) access if console login is not required.")

        for key in user["access_keys"]:
            lines.append("")
            status_note = ""
            if key["never_used"]:
                status_note = " — **FINDING: never used since creation**"
            elif key["stale"]:
                status_note = f" — **FINDING: stale, last used {key['last_used_days_ago']} days ago**"
            lines.append(f"  - Access key `{key['key_id']}` ({key['status']}){status_note}")
            if key["never_used"] or key["stale"]:
                findings_count += 1

        lines.append("")

    # Roles section
    lines.append("## IAM Roles")
    lines.append("")
    lines.append("| Role | Type | Age (days) | Last Used | Finding |")
    lines.append("|---|---|---|---|---|")

    for role in data["roles"]:
        role_type = "AWS service-linked" if role["is_service_linked"] else "Customer-managed"
        last_used = f"{role['last_used_days_ago']}d ago" if role["last_used_days_ago"] is not None else "Never (or not tracked)"
        finding = ""
        if role["stale"] and not role["is_service_linked"]:
            finding = "**Stale — review for removal**"
            findings_count += 1
        elif role["is_service_linked"]:
            finding = "N/A (AWS-managed)"
        else:
            finding = "OK"
        lines.append(f"| {role['role_name']} | {role_type} | {role['account_age_days']} | {last_used} | {finding} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## Summary: {findings_count} finding(s) requiring review")
    lines.append("")
    lines.append("This report should be reviewed by the account owner or designated approver, "
                  "with each finding either remediated, accepted as a documented risk, or scheduled "
                  "for follow-up by a specific date.")

    output_path = f"reports/recertification-report-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.md"
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Recertification report written to {output_path}")
    print(f"Total findings: {findings_count}")


if __name__ == "__main__":
    main()
