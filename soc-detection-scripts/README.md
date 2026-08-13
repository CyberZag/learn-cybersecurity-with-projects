# SOC Detection Scripts

Detection logic, alert queries, and incident response notes drawn from SOC practices — VPN login anomaly detection, CVE-driven patch verification, EDR alert triage, and more.

## Structure

- `splunk/` — SPL searches / detection saved-search templates
- `wazuh/` — Wazuh custom rules and decoders

## Conventions

Each detection file should include a header comment with:

- **Purpose** — what it detects
- **Data source** — index/sourcetype or log source
- **False positive notes** — known benign triggers
- **Response action** — what an analyst should do when it fires
