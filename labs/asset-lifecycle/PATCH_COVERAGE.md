# Which devices missed the update?

A deployment dashboard lists successful installations. The network team also needs to account for devices that stayed offline, checked in late or reported an older update. This exercise compares a synthetic update export with the active devices in the [existing inventory](sample_data.json). It runs locally using Python 3.10 or later and the standard library.

## Run it

From the repository root:

```sh
cd labs/asset-lifecycle
python patch_coverage.py
python -m unittest discover -v
```

The program writes JSON to standard output and leaves the fixture files unchanged. The [saved run](examples/patch-coverage/report.json) was generated from [patch_snapshot.json](patch_snapshot.json). The assistant wrote and tested the code, created the fictional data and generated that output. Learners can record their own predictions, changes and observations separately.

## Read the result

The fixture inventory contains 20 devices. Two are in storage, leaving **18 active devices** in scope for this fictional update. At 17:00 UTC on November 10, three have fresh evidence of installation.

| Result | Active devices | Operator follow-up |
|---|---:|---|
| Installed | 3 | Retain the time and device identifier with the record. |
| Pending | 1 | Check the next maintenance window and follow up after it. |
| Failed | 1 | Inspect the deployment result and assign a retest owner. |
| Stale evidence | 1 | Request a fresh status report. |
| Conflicting reports | 1 | Reconcile the two sources that reported different states at the same instant. |
| No target evidence | 11 | Check reporting coverage, device ownership and the last check-in. |

The remaining 15 devices require different kinds of follow-up. Calling all 15 failed installations would hide a real deployment failure among missing or inconclusive records.

The report also surfaces an unregistered device, a device in storage and a future-dated observation. These exceptions do not expand the denominator. The 72-hour freshness window and shared update target are exercise assumptions. A real fleet needs an applicability assessment and an independently maintained inventory.

## Investigate and retest

1. **A late report arrives.** Copy the snapshot to `learner_snapshot.json`. Predict what changes if CI-007 reports the target update as installed at 16:55 UTC. Add that observation and run `python patch_coverage.py --snapshot learner_snapshot.json`. Explain why its original report for update A could not verify update B.
2. **Two timestamps look different.** Inspect CI-006. Convert the UTC and UTC–05:00 values to the same time zone. Explain the conflict and identify what newer evidence would resolve it.
3. **A report ages out.** Move the review cutoff forward by one second. Identify the device that crosses the freshness boundary and explain why its evidence status changes without a new installation event.
4. **Write the handoff.** Use the failed device and one missing device. For each, record the observation, the next check, the person or team responsible and what would close the ticket. Describe how you would report progress if the device stayed offline.

Six new tests exercise denominator integrity, duplicate delivery, order independence, time zones, evidence freshness, scope exceptions, invalid cutoffs and an empty feed. The full suite passed 56 tests when the assistant ran it. This example compares supplied records and does not inspect a live endpoint or change a device.
