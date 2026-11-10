# IAM access-review exercise

Recovering a departing user's laptop does not remove their application access. This extension reuses the asset lab's fictional user IDs and adds a small role/permission catalogue, a conflict rule and expiring exceptions. It produces an evidence-backed queue for human review. It never revokes access.

**Provenance:** original assistant-authored code and synthetic examples, informed by CleverTailor's Access Appropriate to Role review project suggestion for an IAM role. Assistant test results are not personal learner completion. No employer affiliation or actual directory integration is implied.

## Run and inspect

Python 3.10+; standard library only. From this lab directory:

```sh
python access_review.py --as-of 2026-11-09
python -m unittest -v
```

Read `access_review.json` and `summary.txt` inside the newly printed `access_runs` folder. Inputs and previous runs are preserved. The review date is explicit; the output folder uses the actual UTC execution time.

| Synthetic account | Case | Expected review result |
|---|---|---|
| EXAMPLE-A01 | Clerk can create and approve invoices | Role deviation and separation-of-duties review |
| EXAMPLE-A02 | Reviewer has its listed permissions | No finding under these limited checks |
| EXAMPLE-A03 | Leaver retains an enabled account | Leaver access review |
| EXAMPLE-A04 | Role is absent from the catalogue | Unknown-role data-quality review; do not assume zero entitlement |
| EXAMPLE-A05 | Unmapped permission | Resolve the permission definition |
| EXAMPLE-A06 | Extra permission has an unexpired fictional exception | Record the exception; its authenticity remains unverified |
| EXAMPLE-A07 | Extra permission's exception expired | Expired-exception and role-deviation review |
| EXAMPLE-A08 | Subject absent from the personnel fixture | Reconcile the identity; do not guess its status |

This is a deliberately limited eight-account scope, not the complete access inventory for the twenty fictional users. A disabled account can still retain permission assignments; the program does not model whether those rights are effective or whether sessions remain active.

## Analyst runbook

1. Confirm the review scope, personnel snapshot, role catalogue and scenario date. Record missing owners or mappings as evidence gaps.
2. For a role deviation, inspect the actual business need and approved role definition. Do not infer that every unmatched string should be removed.
3. For a leaver, verify the departure and actual account/session status. Coordinate approved deprovisioning, then obtain separate evidence that it happened.
4. For conflicting permissions, ask the control owner to review the conflict and compensating controls. An exception explaining an extra permission does not automatically resolve the conflict.
5. For an exception, check independent active reviewer, evidence and expiry. These fixture fields are assertions, not authenticated approvals.
6. Record a decision, rationale, owner, due date and evidence reference in your own notes. The software leaves those human decisions to you and makes no invented service-level commitment.
7. Rerun on a copied fixture after a documented synthetic change. Compare findings and explain what changed. A zero-finding result is not certification of compliance.

## Three learner sessions

- **Predict (30 minutes):** classify all eight cases before running the program. Explain why an unknown role is different from excess access.
- **Change and test (45 minutes):** copy `access_review_data.json` to `learner_access.json`. Correct the unknown role, independently justify one exception and introduce a conflicting permission. Run `python access_review.py --scope learner_access.json --as-of 2026-12-01`. Explain expiry-related changes without changing the clock.
- **Investigate (30 minutes):** run the original asset simulation, then review its user data with this extension. Explain why equipment recovery did not eliminate the leaver access finding. Write a short handoff with the next evidence needed.

Record your own commands, changes, observations and explanation in the existing blank learner-evidence file. Until you personally reproduce and explain the work, describe this as an AI-assisted learning resource, not a project you implemented or production IAM experience.

## Corrections and boundaries

The implementation does not copy a generated tutorial's automatic-disable advice, invented remediation deadlines, expected finding counts or legal compliance claims. Unknown roles and permissions receive explicit data-quality findings. Exception expiry is reproducible and does not hide a separation-of-duties conflict. No last-login inactivity rule is asserted because reliable login telemetry is outside this fixture. No Entra tenant, paid licence, cloud account, real identity, private record or gated course asset is required.

Code: [access_review.py](access_review.py). Inputs: [access_review_data.json](access_review_data.json). Tests: [test_access_review.py](test_access_review.py).
