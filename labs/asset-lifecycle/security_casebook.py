"""Three offline security exercises using fictional inputs and local evidence.

Assistant-authored, not learner completion. No network traffic, server, scanning,
account changes, real audit opinion or production-security guarantee.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
from ipaddress import ip_address, ip_network
import json
from pathlib import Path


def evaluate_flow(rules, flow):
    """Model ordered IPv4 TCP/UDP rules; default deny. This is not a firewall."""
    if flow.get('protocol') not in {'tcp', 'udp'}:
        raise ValueError('Only TCP and UDP are modelled')
    port = flow.get('destination_port')
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Valid destination port required')
    source, destination = ip_address(flow['source']), ip_address(flow['destination'])
    if source.version != 4 or destination.version != 4:
        raise ValueError('Only IPv4 is modelled')
    if not isinstance(rules, list):
        raise ValueError('Rules must be a list')
    parsed, ids = [], set()
    for rule in rules:
        rid = rule.get('id')
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError('Unique rule IDs required')
        ids.add(rid)
        if rule.get('action') not in {'allow', 'deny'} or rule.get('protocol') not in {'tcp', 'udp'}:
            raise ValueError('Invalid rule action or protocol')
        ports = rule.get('ports')
        if not isinstance(ports, list) or not ports or any(type(p) is not int or not 1 <= p <= 65535 for p in ports):
            raise ValueError('Rule needs valid destination ports')
        sn, dn = ip_network(rule['source']), ip_network(rule['destination'])
        if sn.version != 4 or dn.version != 4:
            raise ValueError('Only IPv4 rules are modelled')
        parsed.append((rule, sn, dn))
    for rule, sn, dn in parsed:
        if source in sn and destination in dn and flow['protocol'] == rule['protocol'] and port in rule['ports']:
            return {'decision': rule['action'], 'matched_rule': rule['id']}
    return {'decision': 'deny', 'matched_rule': None}


def assess_evidence(records, artifacts, as_of):
    """Check evidence readiness only, under explicitly fictional review criteria.

    Artifacts are supplied bytes, not paths to arbitrary private files. A hash
    match shows consistency with the supplied manifest, not authenticity.
    """
    today = date.fromisoformat(as_of)
    results, ids = [], set()
    for record in records:
        rid = record.get('control_id')
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError('Unique control IDs required')
        ids.add(rid)
        reasons = []
        if not record.get('owner'):
            reasons.append('OWNER_MISSING')
        if record.get('review_status') != 'reviewed':
            reasons.append('REVIEW_NOT_RECORDED')
        if record.get('expected_scope') != record.get('evidence_scope') or not record.get('expected_scope'):
            reasons.append('SCOPE_MISMATCH')
        try:
            collected = date.fromisoformat(record.get('collected_on', ''))
        except (TypeError, ValueError):
            collected = None
        max_age = record.get('max_age_days')
        if type(max_age) is not int or max_age < 0:
            raise ValueError('Explicit nonnegative lab age criterion required')
        if collected is None:
            reasons.append('INVALID_COLLECTION_DATE')
        elif collected > today:
            reasons.append('FUTURE_COLLECTION_DATE')
        elif (today - collected).days > max_age:
            reasons.append('STALE_UNDER_LAB_CRITERION')
        artifact = artifacts.get(record.get('artifact'))
        if artifact is None:
            reasons.append('ARTIFACT_MISSING')
        elif not isinstance(artifact, bytes):
            raise ValueError('Artifacts must be bytes')
        elif hashlib.sha256(artifact).hexdigest() != record.get('sha256'):
            reasons.append('HASH_MISMATCH')
        results.append({'control_id': rid, 'gaps': reasons,
                        'status': 'Evidence gaps require review' if reasons else 'Ready for manual control assessment'})
    return results


def get_record_vulnerable(principal, record_id, records, roles):
    """Deliberately faulty local teaching function: authenticated is not authorized."""
    if principal not in roles:
        return 401, None
    return (200, dict(records[record_id])) if record_id in records else (404, None)


def get_record_authorized(principal, record_id, records, roles):
    """Ownership/role check using a trusted fixture, not client-provided role data.

    Authentication is assumed by this exercise. A real service must authenticate
    the principal and enforce authorization at every relevant server endpoint.
    """
    if principal not in roles:
        return 401, None
    item = records.get(record_id)
    if item is None or (item['owner'] != principal and roles[principal] != 'review_admin'):
        return 404, None
    return 200, dict(item)


def demo(as_of='2026-11-09'):
    # Documentation-only addresses: these strings never become network requests.
    rules = [
        {'id': 'DENY-RESTRICTED', 'source': '192.0.2.0/24', 'destination': '198.51.100.0/25', 'protocol': 'tcp', 'ports': [443], 'action': 'deny'},
        {'id': 'ALLOW-WEB', 'source': '192.0.2.0/24', 'destination': '198.51.100.0/24', 'protocol': 'tcp', 'ports': [443], 'action': 'allow'},
        {'id': 'ALLOW-DNS', 'source': '192.0.2.0/24', 'destination': '203.0.113.53/32', 'protocol': 'udp', 'ports': [53], 'action': 'allow'},
    ]
    flows = [
        {'source': '192.0.2.10', 'destination': '198.51.100.10', 'protocol': 'tcp', 'destination_port': 443},
        {'source': '192.0.2.10', 'destination': '198.51.100.200', 'protocol': 'tcp', 'destination_port': 443},
        {'source': '192.0.2.10', 'destination': '203.0.113.53', 'protocol': 'udp', 'destination_port': 53},
        {'source': '192.0.2.10', 'destination': '198.51.100.200', 'protocol': 'tcp', 'destination_port': 22},
    ]
    evidence = b'SYNTHETIC ONLY: fictional access-review meeting notes.\n'
    good = {'control_id': 'LAB-ACCESS-REVIEW', 'owner': 'Fictional control owner', 'review_status': 'reviewed',
            'expected_scope': 'Eight example accounts', 'evidence_scope': 'Eight example accounts',
            'collected_on': '2026-11-08', 'max_age_days': 30, 'artifact': 'review-notes.txt',
            'sha256': hashlib.sha256(evidence).hexdigest()}
    incomplete = dict(good, control_id='LAB-MISSING-EVIDENCE', artifact='missing.txt', owner='', review_status='pending')
    stale = dict(good, control_id='LAB-OLD-SCOPE', collected_on='2026-08-01', evidence_scope='Different system')
    records = {'EXAMPLE-R1': {'owner': 'U-001', 'content': 'Fictional training note A'},
               'EXAMPLE-R2': {'owner': 'U-002', 'content': 'Fictional training note B'}}
    roles = {'U-001': 'reader', 'U-002': 'reader', 'U-010': 'review_admin'}
    trials = [('U-001', 'EXAMPLE-R1'), ('U-001', 'EXAMPLE-R2'), ('U-010', 'EXAMPLE-R2'), ('UNKNOWN', 'EXAMPLE-R1')]
    return {'synthetic': True, 'as_of': as_of, 'provenance': 'Assistant-authored and tested; not personal learner completion.',
            'network': [{'flow': f, **evaluate_flow(rules, f)} for f in flows],
            'governance': assess_evidence([good, incomplete, stale], {'review-notes.txt': evidence}, as_of),
            'authorization': [{'principal': p, 'record_id': rid,
                               'vulnerable_status': get_record_vulnerable(p, rid, records, roles)[0],
                               'corrected_status': get_record_authorized(p, rid, records, roles)[0]} for p, rid in trials],
            'limitations': ['No live network, firewall, application or third-party system is tested.',
                           'Network model excludes state tracking, NAT, routing, IPv6 and established sessions.',
                           'Evidence readiness is not control effectiveness, audit assurance or regulatory compliance.',
                           'Authorization exercise assumes authenticated principals and trusted role data; not a complete secure application.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', default='2026-11-09')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'casebook_runs')
    args = parser.parse_args()
    report = demo(args.as_of)
    folder = args.output/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'security_casebook.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(folder)


if __name__ == '__main__': main()
