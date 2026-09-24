#!/usr/bin/env python3
"""
IAM Access Review Tool
Pulls all IAM users and roles, checks last-activity, flags stale access
and missing MFA, and produces a structured review report.
"""

import boto3
import json
from datetime import datetime, timezone

STALE_THRESHOLD_DAYS = 90

iam = boto3.client("iam")


def days_since(dt):
    if dt is None:
        return None
    now = datetime.now(timezone.utc)
    return (now - dt).days


def review_users():
    findings = []
    users = iam.list_users()["Users"]

    for user in users:
        username = user["UserName"]
        created = user["CreateDate"]

        # Access keys
        keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]
        key_findings = []
        for key in keys:
            key_id = key["AccessKeyId"]
            last_used_resp = iam.get_access_key_last_used(AccessKeyId=key_id)
            last_used = last_used_resp.get("AccessKeyLastUsed", {}).get("LastUsedDate")
            days = days_since(last_used)
            key_findings.append({
                "key_id": key_id,
                "status": key["Status"],
                "last_used_days_ago": days,
                "stale": days is not None and days > STALE_THRESHOLD_DAYS,
                "never_used": last_used is None,
            })

        # MFA devices
        mfa_devices = iam.list_mfa_devices(UserName=username)["MFADevices"]

        # Console login profile (password-based access)
        has_console_access = True
        try:
            iam.get_login_profile(UserName=username)
        except iam.exceptions.NoSuchEntityException:
            has_console_access = False

        # Attached policies
        attached = iam.list_attached_user_policies(UserName=username)["AttachedPolicies"]

        findings.append({
            "username": username,
            "created": created.isoformat(),
            "account_age_days": days_since(created),
            "has_console_access": has_console_access,
            "mfa_enabled": len(mfa_devices) > 0,
            "access_keys": key_findings,
            "attached_policies": [p["PolicyName"] for p in attached],
        })

    return findings


def review_roles():
    findings = []
    roles = iam.list_roles()["Roles"]

    for role in roles:
        role_name = role["RoleName"]
        created = role["CreateDate"]

        # Skip AWS service-linked roles for last-used detail (not meaningful to review)
        is_service_linked = role_name.startswith("AWSServiceRole")

        # list_roles() does not return RoleLastUsed - it's only populated by
        # get_role() (a per-role call). Confirmed via testing: list_roles()
        # returned no RoleLastUsed field at all for roles known to be actively
        # in use, which would have produced false "stale" findings.
        role_detail = iam.get_role(RoleName=role_name)["Role"]
        last_used_info = role_detail.get("RoleLastUsed", {})
        last_used = last_used_info.get("LastUsedDate")
        days = days_since(last_used)

        findings.append({
            "role_name": role_name,
            "created": created.isoformat(),
            "account_age_days": days_since(created),
            "is_service_linked": is_service_linked,
            "last_used_days_ago": days,
            "never_used": last_used is None,
            "stale": (not is_service_linked) and (days is None or days > STALE_THRESHOLD_DAYS),
        })

    return findings


def main():
    print("Running IAM access review...")
    user_findings = review_users()
    role_findings = review_roles()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stale_threshold_days": STALE_THRESHOLD_DAYS,
        "users": user_findings,
        "roles": role_findings,
    }

    output_path = f"reports/access-review-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report written to {output_path}")
    print(f"Users reviewed: {len(user_findings)}")
    print(f"Roles reviewed: {len(role_findings)}")


if __name__ == "__main__":
    main()
