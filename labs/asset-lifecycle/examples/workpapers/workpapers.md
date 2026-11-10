# Synthetic control-evidence workpapers

Assistant-authored and tested; learner reproduction remains unverified.

As of: 2026-11-10. Three illustrative NIST CSF 2.0 outcomes; not full coverage or a SOC 2 mapping.

Source: https://doi.org/10.6028/NIST.CSWP.29

## LAB-INVENTORY / ID.AM-01

Objective: Maintain a scoped hardware inventory.
Scope: Two fictional devices
Procedure: Reconcile inventory coverage with the fictional two-device population.
Evidence: inventory.txt
Observed gaps: None in the metadata checks
Disposition: Proceed to manual testing
Next action: Manually verify completeness and accuracy against an independent population.
Manual effectiveness assessment: Not performed.
Risk: Unrated. Requires impact and likelihood evidence; not inferred from missing documents.

## LAB-ACCESS / PR.AA-05

Objective: Review permissions against defined least-privilege roles.
Scope: All eight fictional accounts
Procedure: Confirm reviewer ownership, population coverage and recorded review evidence.
Evidence: access.txt
Observed gaps: OWNER_MISSING, REVIEW_NOT_RECORDED, SCOPE_MISMATCH
Disposition: Request evidence
Next action: Request a named reviewer and evidence covering all eight fictional accounts.
Manual effectiveness assessment: Not performed.
Risk: Unrated. Requires impact and likelihood evidence; not inferred from missing documents.

## LAB-RESTORE / RC.RP-03

Objective: Verify integrity of recovery assets before restoration.
Scope: Fictional recovery exercise
Procedure: Inspect the scoped recovery verification artifact and its manifest.
Evidence: restore-test.txt
Observed gaps: ARTIFACT_MISSING
Disposition: Request evidence
Next action: Request actual fictional restore-verification results; a backup claim alone is insufficient.
Manual effectiveness assessment: Not performed.
Risk: Unrated. Requires impact and likelihood evidence; not inferred from missing documents.

## Limits

Manifest consistency does not prove authenticity or control effectiveness.
No audit opinion, compliance conclusion, risk reduction or remediation completion is asserted.
