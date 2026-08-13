#!/usr/bin/env python3
"""
log_parser.py

Quick-triage log parser: reads a plaintext log file and extracts IPv4
addresses, usernames (user=/uid= patterns), and timestamps for fast
eyeballing during incident triage.

Usage:
    python log_parser.py path/to/logfile.log
    python log_parser.py path/to/logfile.log --ips-only
"""

import argparse
import re
import sys
from collections import Counter

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
USER_RE = re.compile(r"(?:user|uid|username)=([\w.\-@]+)", re.IGNORECASE)
TIMESTAMP_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\b|\b\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b"
)


def parse_log(path: str) -> dict:
    ip_counter: Counter = Counter()
    user_counter: Counter = Counter()
    timestamps = []

    with open(path, "r", errors="ignore") as f:
        for line in f:
            ip_counter.update(IPV4_RE.findall(line))
            user_counter.update(USER_RE.findall(line))
            ts_match = TIMESTAMP_RE.search(line)
            if ts_match:
                timestamps.append(ts_match.group())

    return {
        "ips": ip_counter,
        "users": user_counter,
        "first_timestamp": timestamps[0] if timestamps else None,
        "last_timestamp": timestamps[-1] if timestamps else None,
        "line_count_with_ip": sum(ip_counter.values()),
    }


def main():
    parser = argparse.ArgumentParser(description="Quick-triage log parser")
    parser.add_argument("logfile", help="Path to the log file to parse")
    parser.add_argument("--ips-only", action="store_true", help="Only print IP frequency table")
    args = parser.parse_args()

    try:
        result = parse_log(args.logfile)
    except FileNotFoundError:
        print(f"File not found: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    print(f"Time range: {result['first_timestamp']} -> {result['last_timestamp']}")
    print(f"\nTop IPs ({len(result['ips'])} unique):")
    for ip, count in result["ips"].most_common(10):
        print(f"  {ip:<16} {count}")

    if not args.ips_only:
        print(f"\nTop users ({len(result['users'])} unique):")
        for user, count in result["users"].most_common(10):
            print(f"  {user:<20} {count}")


if __name__ == "__main__":
    main()
