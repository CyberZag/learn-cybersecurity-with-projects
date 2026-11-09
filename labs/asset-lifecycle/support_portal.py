"""Read-only support handoff report for the existing synthetic asset lab.

Assistant-authored educational code. No real tickets, messages, accounts or devices.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

from asset_lab import run_demo


def make_report(data):
    """Explain the existing simulator's decisions without changing its rules or inputs."""
    if data.get("synthetic") is not True:
        raise ValueError("This exercise accepts explicitly synthetic data only")
    _, evidence = run_demo(data)
    requests = {ticket["ticket_id"]: ticket for ticket in data["tickets"]}
    rows = []
    for event in evidence["audit"]:
        ticket = requests[event["ticket_id"]]
        applied = event["decision"] == "applied_in_simulation"
        status = "Simulated change complete" if applied else "Held for review"
        reason = event.get("reason", "Approval and current-state checks passed in the simulation")
        if applied:
            next_action = "Review the before/after evidence and confirm the requested outcome. Account-access review is separate."
            response = ("The approved inventory change has completed in this simulation. "
                        "Please review the recorded outcome. This does not confirm any real device action or account-access change.")
        else:
            next_action = "The assigned support analyst should resolve the stated blocker with the appropriate approver or record owner, then reassess."
            response = ("Your request is awaiting review. No inventory change has been applied for this request. "
                        "The next step is to resolve the documented approval or record-state blocker before proceeding.")
        rows.append({
            "ticket_id": ticket["ticket_id"], "asset_id": ticket["asset_id"],
            "operation": ticket["operation"], "status": status, "reason": reason,
            "next_action": next_action, "customer_update_draft": response,
            "priority": "Unassigned: business impact and urgency require review",
            "follow_up": "Agree a follow-up time; no service-level promise is assumed",
            "before": event["before"], "after": event["after"],
        })
    return {"synthetic": True,
            "provenance": "Assistant-authored and tested. Personal learner completion is not claimed.",
            "counts": dict(Counter(row["status"] for row in rows)), "tickets": rows}


def render_html(report):
    """Escape all dataset-derived strings; produce an offline, script-free reference view."""
    def e(value):
        return escape(str(value), quote=True)
    counts = report["counts"]
    cards = []
    for index, row in enumerate(report["tickets"], 1):
        fields = [("Decision evidence", row["reason"]), ("Next action", row["next_action"]),
                  ("Priority", row["priority"]), ("Follow-up", row["follow_up"])]
        details = ''.join(f'<dt>{e(label)}</dt><dd>{e(value)}</dd>' for label, value in fields)
        before = json.dumps(row["before"], indent=2)
        after = json.dumps(row["after"], indent=2)
        cards.append(f'''<article aria-labelledby="ticket-{index}">
<header><h2 id="ticket-{index}">{e(row['ticket_id'])} / {e(row['asset_id'])}</h2>
<span class="status">{e(row['status'])}</span></header>
<p>Requested operation: <strong>{e(row['operation'])}</strong></p><dl>{details}</dl>
<h3>Customer update draft - not sent</h3><blockquote>{e(row['customer_update_draft'])}</blockquote>
<details><summary>Inspect simulated before and after</summary>
<h3>Before</h3><pre>{e(before)}</pre><h3>After</h3><pre>{e(after)}</pre></details></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Synthetic support handoff</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#173144;font:17px/1.55 system-ui,sans-serif}}
main{{max-width:1000px;margin:auto;padding:32px 22px}}h1{{font-size:2.2rem;line-height:1.15;margin:12px 0}}
.notice{{border-left:5px solid #9a5700;background:#fff1d6;padding:14px 18px}}
.metrics{{display:flex;flex-wrap:wrap;gap:14px;margin:24px 0}}.metrics p{{background:#173144;color:white;border-radius:8px;padding:14px 20px;margin:0}}
article{{background:white;border:1px solid #cbd5df;border-radius:10px;padding:24px;margin:22px 0}}
article header{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}h2{{margin:0;font-size:1.35rem}}
h3{{font-size:1rem}}.status{{border:1px solid #61768a;padding:5px 10px;border-radius:5px;font-size:.9rem}}
dt{{font-weight:700;margin-top:14px}}dd{{margin:3px 0 10px}}blockquote{{margin:8px 0;padding:14px 18px;background:#edf3f8;border-left:4px solid #35627c}}
summary{{cursor:pointer;font-weight:650}}summary:focus-visible,a:focus-visible{{outline:3px solid #005b9f;outline-offset:3px}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:12px;font-size:.85rem}}footer{{margin-top:30px;font-size:.95rem}}
@media(max-width:550px){{main{{padding:20px 12px}}article{{padding:16px}}h1{{font-size:1.8rem}}}}
</style></head><body><main><p>OFFLINE LEARNING LAB</p><h1>Support handoff: evidence before action</h1>
<div class="notice"><strong>Synthetic demonstration.</strong> Assistant-authored and tested; not personal learner completion.
No real tickets or messages are sent. No employer affiliation, live system status or response-time promise is implied.</div>
<section aria-label="Example outcomes" class="metrics"><p>{len(report['tickets'])} fictional requests</p>
<p>{counts.get('Simulated change complete',0)} simulated changes complete</p><p>{counts.get('Held for review',0)} held for review</p></section>
<p>Each case uses the existing asset-lifecycle simulator. Read the reason, identify who needs to act next, and compare the evidence before drafting a customer response.</p>
{''.join(cards)}
<footer><strong>Practice:</strong> predict one held request's missing evidence, then repair a copy of the fixture and regenerate.
Record your own work in the learner evidence template. Never paste secrets or real personal or patient data into this exercise.</footer>
</main></body></html>'''


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=base/'sample_data.json')
    parser.add_argument('--output', type=Path, default=base/'support_runs')
    args = parser.parse_args()
    report = make_report(json.loads(args.input.read_text(encoding='utf-8-sig')))
    folder = args.output/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'support_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (folder/'index.html').write_text(render_html(report), encoding='utf-8')
    print(json.dumps({'output':str(folder),'counts':report['counts']},indent=2))


if __name__ == '__main__':
    main()
