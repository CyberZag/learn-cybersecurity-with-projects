# Learn Cybersecurity with Projects

A small collection of original, defensive learning artifacts: a Python log parser and two detection-rule examples.

## Published content

- [`security-tools/log_parser.py`](security-tools/log_parser.py) — extracts IPv4 addresses, usernames, and timestamps from a local plaintext log for quick triage.
- [`soc-detection-scripts/splunk/vpn_login_anomaly.spl`](soc-detection-scripts/splunk/vpn_login_anomaly.spl) — a Splunk search template for reviewing unusual VPN access.
- [`soc-detection-scripts/wazuh/cve_patch_verification_rule.xml`](soc-detection-scripts/wazuh/cve_patch_verification_rule.xml) — a Wazuh rule example for patch-verification workflows.

These are learning examples, not production detections. Validate field names, thresholds, permissions, and response procedures in an authorized environment before use.

## Asset lifecycle practice

- [Asset Lifecycle and Support Ticket Lab](labs/asset-lifecycle/README.md): offline Python exercises connecting inventory records, approval checks, support tickets and leaver follow-up, with synthetic data and ten automated tests.
- [Runbook](labs/asset-lifecycle/RUNBOOK.md) and [learner evidence template](labs/asset-lifecycle/LEARNER_EVIDENCE.md) support practice and a clear explanation of decisions.

This new lab is an AI-assisted learning resource. Its published test results were produced by the assistant; they do not establish personal completion or production experience.

## License

MIT — see [LICENSE](LICENSE).

