"""Offline IAM review of fictional role assignments; no access changes are made.

Original assistant-authored teaching extension. Results are review candidates,
not proof of compliance, risk reduction, learner completion or effective access.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
from pathlib import Path

from asset_lab import validate


def strings(value, label):
    if not isinstance(value, list) or any(not isinstance(s, str) or not s.strip() for s in value):
        raise ValueError(f"{label} must be a list of nonempty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"Duplicate value in {label}")
    return set(value)


def review(inventory, scope, as_of):
    """Return deterministic evidence without mutating either input.

    The explicit review date makes exception expiry reproducible. An exception
    can explain a role deviation, but cannot suppress leaver or SoD findings.
    """
    if not isinstance(inventory, dict) or not isinstance(scope, dict):
        raise ValueError("Inputs must be objects")
    if inventory.get('synthetic') is not True or scope.get('synthetic') is not True:
        raise ValueError("Explicitly synthetic inputs required")
    today = date.fromisoformat(as_of)
    users, _ = validate(inventory)
    catalogue = strings(scope.get('permissions'), 'permissions')
    roles = scope.get('roles')
    if not isinstance(roles, dict) or not roles:
        raise ValueError('Nonempty role catalogue required')
    allowed = {}
    for name, permissions in roles.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Nonempty role name required')
        allowed[name] = strings(permissions, f'role {name}')
        if allowed[name] - catalogue:
            raise ValueError('Role references unknown permission')
    conflicts = scope.get('conflicts')
    if not isinstance(conflicts, list):
        raise ValueError('Conflict rules must be a list')
    pairs = []
    for pair in conflicts:
        p = strings(pair, 'conflict pair')
        if len(p) != 2 or p - catalogue or p in pairs:
            raise ValueError('Conflict rules need unique pairs of known permissions')
        pairs.append(p)
    accounts = scope.get('accounts')
    if not isinstance(accounts, list) or not accounts:
        raise ValueError('Nonempty account review scope required')
    seen = set()
    rows = []
    for account in accounts:
        if not isinstance(account, dict):
            raise ValueError('Account must be an object')
        aid = account.get('account_id')
        if not isinstance(aid, str) or not aid.strip() or aid in seen:
            raise ValueError('Account IDs must be nonempty and unique')
        seen.add(aid)
        uid, role = account.get('user_id'), account.get('role')
        if not isinstance(uid, str) or not uid.strip() or not isinstance(role, str) or not role.strip():
            raise ValueError('Account needs subject ID and role')
        if type(account.get('enabled')) is not bool:
            raise ValueError('Account enabled must be a boolean')
        granted = strings(account.get('permissions'), f'account {aid}')
        issues, exceptions = [], []

        def finding(code, evidence, next_action):
            issues.append({'code': code, 'evidence': evidence, 'next_action': next_action})

        user = users.get(uid)
        if user is None:
            finding('UNKNOWN_SUBJECT', uid, 'Reconcile identity with the authoritative personnel record; do not infer employment status.')
        elif user['status'] == 'leaver' and (account['enabled'] or granted):
            finding('LEAVER_ACCESS_REVIEW', {'enabled': account['enabled'], 'assigned_permissions': sorted(granted)},
                    'Verify departure and actual effective access; coordinate approved deprovisioning and collect evidence.')
        if role not in allowed:
            finding('UNKNOWN_ROLE', role, 'Have the role owner validate the mapping before deciding which access is excessive.')
        unknown = granted - catalogue
        if unknown:
            finding('UNKNOWN_PERMISSION', sorted(unknown), 'Resolve permission definitions with the application owner.')
        for pair in pairs:
            if pair <= granted:
                finding('SEPARATION_OF_DUTIES_REVIEW', sorted(pair), 'Review the conflicting assignment and any compensating control; do not auto-revoke.')

        exception_rows = account.get('exceptions', [])
        if not isinstance(exception_rows, list):
            raise ValueError('Exceptions must be a list')
        explained, exception_permissions = set(), set()
        for exception in exception_rows:
            if not isinstance(exception, dict):
                raise ValueError('Exception must be an object')
            permission = exception.get('permission')
            if not isinstance(permission, str) or not permission.strip():
                raise ValueError('Exception requires a permission')
            if permission in exception_permissions:
                raise ValueError('Duplicate exception for permission')
            exception_permissions.add(permission)
            reviewer = exception.get('reviewer_id')
            valid = permission in catalogue and permission in granted and isinstance(reviewer, str) and reviewer in users and reviewer != uid
            valid = valid and users[reviewer]['status'] == 'active'
            valid = valid and isinstance(exception.get('evidence'), str) and bool(exception['evidence'].strip())
            try:
                expiry = date.fromisoformat(exception.get('expires_on', ''))
            except (ValueError, TypeError):
                expiry = None
            if not valid or expiry is None:
                finding('INVALID_EXCEPTION', permission, 'Obtain independent active-owner review, a defined expiry and supporting evidence.')
            elif expiry < today:
                finding('EXPIRED_EXCEPTION', {'permission': permission, 'expires_on': expiry.isoformat()},
                        'Reassess the business need; an expired exception does not explain current access.')
            else:
                explained.add(permission)
                exceptions.append({'permission': permission, 'reviewer_id': reviewer,
                                   'expires_on': expiry.isoformat(), 'evidence': exception['evidence'],
                                   'status': 'Fictional exception recorded; authenticity not verified'})
        if role in allowed:
            excess = (granted & catalogue) - allowed[role] - explained
            if excess:
                finding('ROLE_DEVIATION_REVIEW', sorted(excess),
                        'Validate business need and role ownership; record a reviewed decision before changing access.')
        rows.append({'account_id': aid, 'user_id': uid, 'role': role, 'enabled': account['enabled'],
                     'status': 'Review required' if issues else 'No finding under these limited checks',
                     'findings': issues, 'recorded_exceptions': exceptions})
    return {'synthetic': True, 'as_of': today.isoformat(),
            'provenance': 'Assistant-authored and tested; not personal learner completion.',
            'scope': {'accounts_reviewed': len(rows), 'inventory_users': len(users),
                      'coverage': 'Only listed accounts and explicit fixture rules; not complete identity coverage.'},
            'limitations': ['No directory connection or change. Disabled accounts may retain assignments.',
                           'Effective access, group nesting, session tokens, exception authenticity and policy completeness are not verified.',
                           'No finding is not approval or proof of compliance. All decisions require human review.'],
            'finding_counts': dict(sorted(Counter(f['code'] for r in rows for f in r['findings']).items())),
            'accounts': rows}


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=base/'sample_data.json')
    parser.add_argument('--scope', type=Path, default=base/'access_review_data.json')
    parser.add_argument('--as-of', default='2026-11-09', help='Explicit scenario date, YYYY-MM-DD')
    parser.add_argument('--output', type=Path, default=base/'access_runs')
    args = parser.parse_args()
    report = review(json.loads(args.inventory.read_text(encoding='utf-8-sig')),
                    json.loads(args.scope.read_text(encoding='utf-8-sig')), args.as_of)
    folder = args.output/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'access_review.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    lines = ['SYNTHETIC IAM ACCESS REVIEW', report['provenance'], f"Scenario date: {report['as_of']}"]
    for row in report['accounts']:
        lines.append(f"{row['account_id']}: {row['status']}")
        lines.extend(f"  {f['code']}: {f['evidence']} | {f['next_action']}" for f in row['findings'])
    lines.extend(report['limitations'])
    (folder/'summary.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(folder), 'findings': report['finding_counts']}, indent=2))


if __name__ == '__main__':
    main()
