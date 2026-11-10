# Network, GRC and application-security practice

Three small runnable exercises complement the [IAM access review](ACCESS_REVIEW.md). They share a focus on explaining evidence before making a security decision. All identifiers, records, rules and evidence are fictional. Code and example results are assistant-authored and tested; they do not establish personal learner completion.

## Run

Python 3.10+ and the standard library only:

```sh
python security_casebook.py --as-of 2026-11-09
python -m unittest -v
```

Read `security_casebook.json` in the new `casebook_runs` directory. Every run gets a new folder. Nothing is sent over a network. The input cases live in `demo()` in [security_casebook.py](security_casebook.py); edit a copy when practising.

## Network administration: explain an access path

The ordered-rule model evaluates a source address, destination address, transport and destination port. The first matching rule determines the result; unmatched flows are denied in this exercise. Documentation-only IP addresses are plain data, never connection targets.

Expected example outcomes: deny HTTPS to the restricted destination subnet, allow HTTPS to the other example web destination, allow UDP DNS to the listed resolver, and deny unmatched SSH.

**Practice, 45 minutes:** predict the four decisions, run the program, then swap the first two rules in your copy. Explain why the broader allow can hide the restricted-subnet denial. Add one allowed management flow limited to a single fictional host and port. Add a regression test that another source is still denied. Write the expected change, approval needed, verification evidence and rollback step.

**Troubleshooting handoff:** distinguish policy evaluation from whether a service is reachable. A real investigation also needs DNS resolution, routing, NAT, return-path/state handling, endpoint service status and authorized packet/log evidence. This model does not implement those systems, IPv6 or a production firewall. Do not call its output a live connectivity test or firewall deployment.

## GRC / control assurance: check evidence readiness

The evidence checker compares a fictional manifest with in-memory artifact bytes. It flags absent owner/review, scope mismatch, missing or changed artifact, invalid/future collection date, and evidence older than an explicitly chosen lab threshold.

**Practice, 45 minutes:** explain why a matching file hash does not prove authenticity or operating effectiveness. Predict the three control cases, then change the artifact bytes without updating the manifest. Re-run and explain the hash finding. Reconcile an incorrect scope statement and document what evidence would actually demonstrate the control operated. Do not simply replace the expected hash to make a test pass.

Create a short control-testing workpaper with: objective, population/scope, period, owner, evidence reference, procedure performed, result, limitation and follow-up. Separate design questions from evidence of actual operation. The 30-day age threshold is an arbitrary exercise setting, not a regulatory requirement. The result “Ready for manual control assessment” is deliberately not an audit opinion or compliance certification.

For vendor-risk practice, make a fictional evidence request that specifies system scope and period. Explain how an incomplete response changes the follow-up questions. No real vendor or personal records belong in this fixture.

## Junior pentesting / application security: object-level authorization

`get_record_vulnerable()` deliberately checks that a fictional principal is known but does not verify ownership of the requested record. A different reader can retrieve the example object. `get_record_authorized()` checks ownership or a trusted reviewer role and returns no object for unauthorized requests.

This is a local function-level reproduction, not a network exploit or a complete web application. There is no server, credential, scan or real target. Authentication is assumed by the fixture. A production system would require authenticated principals, trusted role lookup and consistent server-side enforcement on every affected endpoint.

**Practice, 45 minutes:** reproduce the cross-user read locally. Write a finding with scope, exact reproduction steps, expected/actual result, fictional impact, root cause, remediation and retest evidence. Compare the owner, other reader, authorized reviewer, unknown principal and missing-record cases. Add a test that a caller-controlled claim such as “admin” cannot grant access without a trusted role entry. Explain why unpredictable IDs alone are insufficient authorization.

Do not scan public websites or repurpose this exercise against systems without permission. Report the observed limited behavior, not a fabricated severity score or real data breach.

## Evidence and interview use

Keep your own predictions, commands, edited files, test output and explanation in the existing learner-evidence template. The assistant's passing tests remain separately attributed. Explain what the model cannot prove as clearly as what it demonstrates. Only add completed-exercise wording to a résumé after you personally run, modify and explain the relevant work.
