# Support and asset review runbook


1. Intake: capture the ticket, affected asset, user, business impact and requested operation. Separate reported symptoms from verified observations. A missing record is a data-quality question, not proof of a breach.
2. Verify context: confirm the asset ID, current status, assignee and authoritative user status. In this exercise JSON is the fictional source; in a real organization approved records and staff verification would be needed.
3. Approval: require a different active approver plus supporting evidence under this lab's policy. Text in an approval field is NOT authentication. The demonstration does not establish that a person actually approved anything.
4. Check for change: compare expected status and assignee with current state. Hold stale requests for re-review rather than overwrite newer information.
5. Deploy/transfer: require an active recipient and an appropriate lifecycle state. Record before/after, ticket, approver and evidence.
6. Reclaim: coordinate verified recovery; move recovered equipment to inspection/repair, unassigned. Do not assume it is sanitized or ready to redeploy. A separate authorized review must address accounts, sessions, groups, applications and data retention as applicable. This script does none of those actions.
7. Retire: require unassigned equipment plus recorded sanitization/disposal evidence. The string in this synthetic exercise is illustrative; it is not proof of an actual wipe. No device is wiped.
8. Close: use resolution notes and evidence. For held requests, explain the missing approval or state conflict and the next responsible person. Do not invent an SLA, incident priority, repair or user confirmation.

EXAMPLE INVESTIGATION PROMPT
CI-003 remains assigned to synthetic leaver U-003. Review T-003. Explain why recovering that asset can close the inventory finding while account access may still need review. State what evidence you would request before taking any real action.

LIMITATIONS TO DISCUSS
This is a small relational inventory simulation, not an enterprise CMDB with discovery, dependency maps, authenticated roles, concurrency control, immutable audit storage or ITSM integrations. The local JSON audit can be edited and must not be described as tamper-proof. The fixed event time is fictional and separate from the actual run folder timestamp.
