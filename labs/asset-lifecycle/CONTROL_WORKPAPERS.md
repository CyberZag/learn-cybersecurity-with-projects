# Control-evidence workpapers for a fictional SaaS team

An analyst needs to explain what the evidence supports, what remains unknown and who should act next. This original offline exercise extends the existing evidence checker with reviewable workpapers. All examples are synthetic; code and results are assistant-authored and tested. Learner completion is not claimed.

## Run and inspect

Requires Python 3.10+ and the standard library. From this lab directory:

```sh
python control_workpaper.py --as-of 2026-11-10
python -m unittest -v
```

Each run creates a new folder in `workpaper_runs/`, preserving earlier output. Inspect `workpapers.json` and `workpapers.md`. The fixture uses in-memory bytes and does not read private documents, contact an employer, access a cloud tenant or change accounts.

The three cases produce one workpaper ready for **manual testing** and two evidence requests:

| Fictional case | Observation | Next investigation |
|---|---|---|
| Hardware inventory | Manifest checks pass for two devices | Reconcile with an independently established population and verify actual accuracy |
| Access review | Owner missing, review pending, scope covers two of eight accounts | Obtain an accountable reviewer and population-complete evidence |
| Recovery verification | Artifact missing | Obtain results of recovery-asset verification; a backup assertion is insufficient |

These are evidence-readiness observations. Missing paperwork alone does not establish that a control failed or that an incident occurred. A passing hash check establishes consistency with a supplied manifest, not authenticity. Ratings remain unset until a reviewer has justified likelihood and impact.

## Framework references and boundaries

The mapping uses three outcomes from [NIST CSF 2.0, NIST CSWP 29](https://doi.org/10.6028/NIST.CSWP.29), published February 26, 2024:

- ID.AM-01: maintaining hardware inventory.
- PR.AA-05: managing and reviewing permissions, including least privilege and separation of duties.
- RC.RP-03: checking integrity of recovery assets before restoration.

These short descriptions are paraphrases. Read the official outcome and decide which evidence would address it in the selected scope. This is a narrow illustrative mapping; it is not complete CSF coverage, a SOC 2 criteria mapping or an assurance opinion.

## Guided practice, 60 minutes

1. **Predict, 10 minutes.** Read `fixture()` before running. Write the expected gaps and distinguish incomplete evidence from a failed control.
2. **Reproduce, 10 minutes.** Run the exercise and compare your predictions. Record the actual command, date and output in your learner evidence file.
3. **Investigate, 15 minutes.** Change the inventory artifact without changing its manifest. Explain the new hash finding. Do not silently replace the hash to make it pass.
4. **Repair and retest, 15 minutes.** In a separate copy, provide a clearly fictional reviewer, revised full-population artifact, accurate manifest and review evidence for the access case. Explain how the new bytes demonstrate coverage. Changing only the scope label can satisfy metadata checks without improving the evidence; document that limitation explicitly.
5. **Communicate, 10 minutes.** Write an unsent evidence request specifying the objective, population, period, owner, exact artifact and secure delivery method. Draft a five-sentence status update that separates observed facts, unknowns, recommended action and ownership.

For interview practice, explain why a missing restore-test artifact is different from a failed restore, why a hash is not proof of authenticity, and what evidence would support a conclusion about operating effectiveness. Do not claim to have audited a real organization.

## Verification and attribution

The assistant ran the full suite on November 10, 2026: **50 tests passed** (43 existing plus seven workpaper tests). Tests cover distinct gaps, changed artifacts, partial remediation, complete metadata retest, missing context, unchanged inputs and explicit absence of an effectiveness conclusion or invented risk score. Example files are under `examples/workpapers/`.

The idea was prompted by a CleverTailor project recommendation. This implementation is original and deliberately narrower: it reuses the existing lab, avoids forced risk scores, makes no audit-readiness forecast, and keeps learner completion blank until personally reproduced. It does not republish the generated tutorial or any gated course material.
