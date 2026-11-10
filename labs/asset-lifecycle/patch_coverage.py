"""Reconcile a fictional update report against the existing asset inventory."""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from asset_lab import validate


HERE = Path(__file__).resolve().parent
STATES = {"installed", "pending", "failed"}


def instant(value):
    if not isinstance(value, str):
        raise ValueError("A timestamp must be a string with a time zone")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() is None:
        raise ValueError("A timestamp must include a time zone")
    return result.astimezone(timezone.utc)


def reconcile(inventory, snapshot):
    validate(inventory)
    cutoff = instant(snapshot["as_of"])
    hours = snapshot["freshness_hours"]
    if type(hours) is not int or not 1 <= hours <= 8760:
        raise ValueError("freshness_hours must be a positive integer up to one year")
    update = snapshot["target_update"]
    if not isinstance(update, str) or not update.strip():
        raise ValueError("target_update must identify the update under review")
    active = {a["asset_id"] for a in inventory["assets"] if a["status"] == "active"}
    known = {a["asset_id"] for a in inventory["assets"]}
    reports = defaultdict(list)
    exceptions = set()
    for event in snapshot["reports"]:
        device, status = event["asset_id"], event["state"]
        if not isinstance(device, str) or not device.strip() or status not in STATES:
            raise ValueError("Invalid asset ID or report state")
        at = instant(event["observed_at"])
        if event["update"] != update:
            continue
        if device not in known:
            reason = "unregistered asset"
        elif device not in active:
            reason = "outside active scope"
        elif at > cutoff:
            reason = "timestamp after review cutoff"
        else:
            reports[device].append((at, status))
            continue
        exceptions.add((device, reason))

    decisions = []
    for device in sorted(active):
        observations = reports[device]
        latest = max((at for at, _ in observations), default=None)
        states = {state for at, state in observations if at == latest}
        if latest is None:
            result = "no target evidence"
        elif len(states) > 1:
            result = "conflicting reports"
        elif cutoff - latest > timedelta(hours=hours):
            result = "stale evidence"
        else:
            result = states.pop()
        decisions.append({"asset_id": device, "result": result,
                          "latest_utc": latest.isoformat() if latest else None})
    counts = Counter(row["result"] for row in decisions)
    return {"target_update": update, "as_of": cutoff.isoformat(),
            "active_devices": len(active), "verified_installed": counts["installed"],
            "by_state": dict(sorted(counts.items())), "devices": decisions,
            "exceptions": [{"asset_id": device, "reason": reason}
                           for device, reason in sorted(exceptions)]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=HERE / "sample_data.json")
    parser.add_argument("--snapshot", type=Path, default=HERE / "patch_snapshot.json")
    args = parser.parse_args()
    result = reconcile(json.loads(args.inventory.read_text(encoding="utf-8")),
                       json.loads(args.snapshot.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
