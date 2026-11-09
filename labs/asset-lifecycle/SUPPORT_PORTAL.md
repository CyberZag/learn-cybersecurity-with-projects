# Support handoff extension

The existing inventory exercise now has an offline HTML view and structured support report. It reuses the five existing fictional requests and their actual simulator outcomes. A held request is never described as resolved.

**Provenance:** original assistant-authored implementation, informed by CleverTailor suggestions for a client support portal and ticket simulation. Test execution and example results belong to the assistant. They do not establish Zagros's personal completion, professional helpdesk experience or familiarity with an employer's software.

## Run

Requires Python 3.10+ and only its standard library. From this lab directory:

```sh
python support_portal.py
python -m unittest -v
```

Open `index.html` in the newly printed `support_runs` folder. The matching `support_report.json` is the underlying evidence. Each run creates a new folder and preserves the input and earlier output. There is no server, JavaScript, network request, message-sending feature or data-entry form.

## What to inspect

- Five requests: two simulated inventory changes complete and three held for review.
- The stated reason is taken from the existing approval and record-state checks.
- Before/after evidence remains identical on held requests.
- Customer updates are unsent drafts. Review them before any real-world adaptation.
- Priority remains unassigned because business impact and urgency were not provided. An urgent request alone does not establish a critical outage.
- No response-time, service availability, device repair, account revocation or user-confirmed resolution is invented.

The fixture must have `synthetic: true`; this marker is only a guard against accidental use, not a detector of private information. Use fictional data exclusively. The HTML escapes dataset-derived text, and a restrictive content policy blocks external resources and forms. This is a small local teaching example, not a secured multi-user helpdesk.

## Two 30-minute learner sessions

1. Predict each case's status without running it. Explain why recovering an asset does not revoke account access. Run the tool and compare your predictions.
2. Copy `sample_data.json` to `learner_data.json`. Repair one held request's evidence with clearly fictional information and make another request stale. Run `python support_portal.py --input learner_data.json`. Explain which results changed and why.

Record your actual commands, changes, observations and explanation in `LEARNER_EVIDENCE.md` (or the local `.txt` version). The original learner record remains blank. Do not claim this exercise on a résumé as completed until you personally run, change and explain it.

## Apply the ideas to support interviews

For a client-support role, explain how the next action and owner are communicated without pretending the issue is fixed. For a healthcare-support role, explain why diagnostic notes must exclude unnecessary patient data and why security/privacy concerns go through the organization's approved escalation process. This lab contains no clinical, EMR or billing workflow, no legal compliance determination, and no real patient information.

## Corrections to generated project suggestions

The adaptation avoids employer branding, invented system-health banners, fake response-time commitments, nonfunctional ticket forms, real-looking contact addresses, unverified vendor-specific password-reset steps, and claims that merely receiving a tutorial proves completed work. No paid plan, new account, external message or live-system action is needed.
