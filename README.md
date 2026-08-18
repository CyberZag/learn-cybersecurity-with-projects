# Learn Cybersecurity with Projects

A small collection of original, defensive learning artifacts: a Python log parser and two detection-rule examples.

## Published content

- [`security-tools/log_parser.py`](security-tools/log_parser.py) — extracts IPv4 addresses, usernames, and timestamps from a local plaintext log for quick triage.
- [`soc-detection-scripts/splunk/vpn_login_anomaly.spl`](soc-detection-scripts/splunk/vpn_login_anomaly.spl) — a Splunk search template for reviewing unusual VPN access.
- [`soc-detection-scripts/wazuh/cve_patch_verification_rule.xml`](soc-detection-scripts/wazuh/cve_patch_verification_rule.xml) — a Wazuh rule example for patch-verification workflows.

These are learning examples, not production detections. Validate field names, thresholds, permissions, and response procedures in an authorized environment before use.

## License

MIT — see [LICENSE](LICENSE).
