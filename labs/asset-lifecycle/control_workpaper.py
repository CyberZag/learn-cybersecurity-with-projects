"""Offline control-evidence workpapers; synthetic, assistant-authored examples.

Reuses the evidence checker. No audit opinion, live system access or learner
completion is implied. All input bytes are constructed here, never private files.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from security_casebook import assess_evidence

SOURCE = 'https://doi.org/10.6028/NIST.CSWP.29'


def fixture():
    artifacts = {'inventory.txt': b'SYNTHETIC: two fictional devices D-01 and D-02; owner operations.\n',
                 'access.txt': b'SYNTHETIC: review covers sample accounts only, not the full population.\n'}
    common = {'owner': 'Fictional operations owner', 'review_status': 'reviewed',
              'collected_on': '2026-11-08', 'max_age_days': 30}
    records = [
        dict(common, control_id='LAB-INVENTORY', artifact='inventory.txt', expected_scope='Two fictional devices',
             evidence_scope='Two fictional devices', sha256=hashlib.sha256(artifacts['inventory.txt']).hexdigest()),
        dict(common, control_id='LAB-ACCESS', artifact='access.txt', expected_scope='All eight fictional accounts',
             evidence_scope='Two sample accounts', owner='', review_status='pending',
             sha256=hashlib.sha256(artifacts['access.txt']).hexdigest()),
        dict(common, control_id='LAB-RESTORE', artifact='restore-test.txt', expected_scope='Fictional recovery exercise',
             evidence_scope='Fictional recovery exercise', sha256='0'*64),
    ]
    metadata = {
        'LAB-INVENTORY': {'reference': 'ID.AM-01', 'objective': 'Maintain a scoped hardware inventory.',
                         'procedure': 'Reconcile inventory coverage with the fictional two-device population.',
                         'next_action': 'Manually verify completeness and accuracy against an independent population.'},
        'LAB-ACCESS': {'reference': 'PR.AA-05', 'objective': 'Review permissions against defined least-privilege roles.',
                      'procedure': 'Confirm reviewer ownership, population coverage and recorded review evidence.',
                      'next_action': 'Request a named reviewer and evidence covering all eight fictional accounts.'},
        'LAB-RESTORE': {'reference': 'RC.RP-03', 'objective': 'Verify integrity of recovery assets before restoration.',
                       'procedure': 'Inspect the scoped recovery verification artifact and its manifest.',
                       'next_action': 'Request actual fictional restore-verification results; a backup claim alone is insufficient.'},
    }
    return records, artifacts, metadata


def build_workpapers(records, artifacts, metadata, as_of):
    results = assess_evidence(records, artifacts, as_of)
    if set(metadata) != {r['control_id'] for r in records}:
        raise ValueError('Metadata must match the complete control population')
    papers = []
    for record, result in zip(records, results):
        meta = metadata[record['control_id']]
        if any(not isinstance(meta.get(k), str) or not meta[k].strip()
               for k in ['reference', 'objective', 'procedure', 'next_action']):
            raise ValueError('Complete workpaper context required')
        papers.append({**deepcopy(meta), **result,
                       'scope': record['expected_scope'], 'evidence_reference': record['artifact'],
                       'owner': record['owner'] or None,
                       'manual_effectiveness_assessment': 'Not performed',
                       'risk_rating': None, 'risk_rationale': 'Requires impact and likelihood evidence; not inferred from missing documents.',
                       'disposition': 'Request evidence' if result['gaps'] else 'Proceed to manual testing'})
    return {'synthetic': True, 'as_of': as_of,
            'provenance': 'Assistant-authored and tested; learner reproduction remains unverified.',
            'framework_source': SOURCE, 'mapping_scope': 'Three illustrative NIST CSF 2.0 outcomes; not full coverage or a SOC 2 mapping.',
            'workpapers': papers, 'summary': {'total': len(papers),
                'evidence_requests': sum(bool(p['gaps']) for p in papers),
                'ready_for_manual_testing': sum(not p['gaps'] for p in papers)},
            'limitations': ['Manifest consistency does not prove authenticity or control effectiveness.',
                            'No audit opinion, compliance conclusion, risk reduction or remediation completion is asserted.']}


def render(report):
    lines = ['# Synthetic control-evidence workpapers', '', report['provenance'], '',
             f"As of: {report['as_of']}. {report['mapping_scope']}", '',
             f"Source: {report['framework_source']}", '']
    for paper in report['workpapers']:
        lines += [f"## {paper['control_id']} / {paper['reference']}", '',
                  f"Objective: {paper['objective']}", f"Scope: {paper['scope']}",
                  f"Procedure: {paper['procedure']}", f"Evidence: {paper['evidence_reference']}",
                  f"Observed gaps: {', '.join(paper['gaps']) or 'None in the metadata checks'}",
                  f"Disposition: {paper['disposition']}", f"Next action: {paper['next_action']}",
                  'Manual effectiveness assessment: Not performed.',
                  f"Risk: Unrated. {paper['risk_rationale']}", '']
    return '\n'.join(lines + ['## Limits', ''] + report['limitations']) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', default='2026-11-10')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'workpaper_runs')
    args = parser.parse_args()
    report = build_workpapers(*fixture(), args.as_of)
    folder = args.output/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'workpapers.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    (folder/'workpapers.md').write_text(render(report), encoding='utf-8')
    print(folder)


if __name__ == '__main__': main()
