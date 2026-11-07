"""Offline, synthetic IT asset and approval workflow. AI-assisted educational demo.

No network calls, real accounts, authentication, BMC/Intune integration or device changes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

ASSET_STATES = {"storage", "active", "repair", "retired"}
USER_STATES = {"active", "leaver"}
OPERATIONS = {"deploy", "transfer", "reclaim", "retire"}


def validate(data):
    """Reject ambiguous identifiers and broken relationships before simulating changes."""
    if not isinstance(data, dict):
        raise ValueError("Dataset must be an object")
    for collection, key in [("users", "user_id"), ("assets", "asset_id"), ("tickets", "ticket_id")]:
        rows = data.get(collection)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"{collection} must be a nonempty list")
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Each {collection} row needs a nonempty {key}")
            if row[key] in seen:
                raise ValueError(f"Duplicate {key}: {row[key]}")
            seen.add(row[key])
    users = {u["user_id"]: u for u in data["users"]}
    assets = {a["asset_id"]: a for a in data["assets"]}
    for user in users.values():
        if user.get("status") not in USER_STATES:
            raise ValueError(f"Invalid user status: {user['user_id']}")
    for asset in assets.values():
        if asset.get("status") not in ASSET_STATES:
            raise ValueError(f"Invalid asset status: {asset['asset_id']}")
        if asset.get("assigned_to") is not None and asset["assigned_to"] not in users:
            raise ValueError(f"Unknown assignee: {asset['asset_id']}")
        if asset["status"] == "active" and asset.get("assigned_to") is None:
            raise ValueError(f"Active asset has no assignee: {asset['asset_id']}")
        if asset["status"] in {"storage", "retired"} and asset.get("assigned_to") is not None:
            raise ValueError(f"Unassigned lifecycle state has an assignee: {asset['asset_id']}")
    for ticket in data["tickets"]:
        if ticket.get("asset_id") not in assets:
            raise ValueError(f"Unknown asset on ticket: {ticket['ticket_id']}")
        if ticket.get("operation") not in OPERATIONS:
            raise ValueError(f"Invalid operation: {ticket['ticket_id']}")
        if ticket.get("status") not in {"open", "closed"}:
            raise ValueError(f"Invalid ticket status: {ticket['ticket_id']}")
        for key in ["requested_by", "approved_by", "to_user"]:
            value = ticket.get(key)
            if value is not None and value not in users:
                raise ValueError(f"Unknown {key}: {ticket['ticket_id']}")
    return users, assets


def findings(data):
    users, _ = validate(data)
    issues = []
    for asset in data["assets"]:
        assignee = asset.get("assigned_to")
        if assignee and users[assignee]["status"] == "leaver":
            issues.append({"code": "ASSET_ASSIGNED_TO_LEAVER", "asset_id": asset["asset_id"],
                           "user_id": assignee, "action": "Verify departure and coordinate approved asset recovery; review access separately."})
    return issues


def apply_ticket(data, ticket_id, when):
    """Apply one already-approved SIMULATED operation; return a new state plus evidence.

    Approval fields are fictional inputs, not an identity or authorization system.
    Policy checks are explicit lab choices, not a claim of ITIL/BMC compliance.
    """
    users, _ = validate(data)
    result = deepcopy(data)
    tickets = {t["ticket_id"]: t for t in result["tickets"]}
    assets = {a["asset_id"]: a for a in result["assets"]}
    if ticket_id not in tickets:
        raise ValueError("Unknown ticket")
    ticket = tickets[ticket_id]
    asset = assets[ticket["asset_id"]]
    before = deepcopy(asset)
    reason = None
    requester, approver = ticket.get("requested_by"), ticket.get("approved_by")
    target = ticket.get("to_user")
    op = ticket["operation"]
    if ticket["status"] != "open":
        reason = "Ticket already closed; replay refused"
    elif not requester or not approver or users[approver]["status"] != "active":
        reason = "Active approver and known requester required"
    elif requester == approver:
        reason = "Requester cannot approve their own change in this lab"
    elif not isinstance(ticket.get("evidence"), str) or not ticket["evidence"].strip():
        reason = "Supporting evidence required"
    elif asset["status"] != ticket.get("expected_status") or asset.get("assigned_to") != ticket.get("expected_assignee"):
        reason = "Asset changed since request; review the stale request"
    elif op in {"deploy", "transfer"} and (not target or users[target]["status"] != "active"):
        reason = "Deployment or transfer requires an active recipient"
    elif op == "deploy" and asset["status"] != "storage":
        reason = "Only an asset in storage may be deployed"
    elif op == "transfer" and asset["status"] != "active":
        reason = "Only an active asset may be transferred"
    elif op == "reclaim" and asset["status"] not in {"active", "repair"}:
        reason = "Only active or repair assets may be reclaimed"
    elif op == "retire" and (asset["status"] not in {"storage", "repair"} or asset.get("assigned_to") is not None):
        reason = "Retirement requires an unassigned storage or repair asset"
    elif op == "retire" and not ticket.get("sanitization_evidence"):
        reason = "Sanitization and disposal evidence required; no wipe is performed by this demo"
    if reason:
        return deepcopy(data), {"ticket_id": ticket_id, "decision": "blocked", "reason": reason,
                                "time_utc": when, "before": before, "after": before}
    if op in {"deploy", "transfer"}:
        asset.update(status="active", assigned_to=target)
    elif op == "reclaim":
        # Recovered assets go into inspection/repair, not straight back to deployable storage.
        asset.update(status="repair", assigned_to=None)
    else:
        asset.update(status="retired", assigned_to=None)
    asset["last_updated"] = when
    ticket.update(status="closed", closed_at=when,
                  resolution=f"Simulated {op}; evidence: {ticket['evidence']}")
    validate(result)
    return result, {"ticket_id": ticket_id, "decision": "applied_in_simulation", "operation": op,
                    "time_utc": when, "approver": approver, "evidence": ticket["evidence"],
                    "before": before, "after": deepcopy(asset)}


def run_demo(data):
    validate(data)
    current = deepcopy(data)
    before = findings(current)
    audit = []
    for t in data["tickets"]:
        current, event = apply_ticket(current, t["ticket_id"], "2026-11-06T15:00:00Z")
        audit.append(event)
    return current, {"provenance": "AI-assisted demo; assistant run is not learner completion",
                     "synthetic": True, "findings_before": before, "findings_after": findings(current),
                     "asset_counts": dict(Counter(a["status"] for a in current["assets"])), "audit": audit}


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base/"sample_data.json")
    parser.add_argument("--output", type=Path, default=base/"runs")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    final, report = run_demo(data)
    # Each run gets a new folder; input and earlier evidence are never overwritten.
    folder = args.output/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    folder.mkdir(parents=True, exist_ok=False)
    (folder/"report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (folder/"simulated_final_state.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    lines=["SYNTHETIC ASSET LIFECYCLE LAB", "AI-assisted resource; this run alone does not establish learner completion.",
           f"Assets: {len(final['assets'])}; users: {len(final['users'])}",
           f"Leaver-assignment findings: {len(report['findings_before'])} before / {len(report['findings_after'])} after", ""]
    lines += [f"{e['ticket_id']}: {e['decision']} - {e.get('reason',e.get('operation'))}" for e in report["audit"]]
    lines += ["", "Reclaiming an asset does NOT revoke account access. This lab makes no account or device changes.", f"Evidence folder: {folder}"]
    (folder/"summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
