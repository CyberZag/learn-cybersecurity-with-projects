from copy import deepcopy
from datetime import date
import hashlib
import unittest

from security_casebook import assess_evidence, demo, evaluate_flow, get_record_authorized, get_record_vulnerable


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.flow = {'source': '192.0.2.5', 'destination': '198.51.100.8', 'protocol': 'tcp', 'destination_port': 443}
        self.rule = {'id': 'WEB', 'source': '192.0.2.0/24', 'destination': '198.51.100.0/24', 'protocol': 'tcp', 'ports': [443], 'action': 'allow'}

    def test_default_deny_and_exact_tuple(self):
        self.assertEqual(evaluate_flow([], self.flow)['decision'], 'deny')
        self.assertEqual(evaluate_flow([self.rule], self.flow)['decision'], 'allow')
        for patch in [{'source': '203.0.113.2'}, {'destination': '203.0.113.4'}, {'protocol': 'udp'}, {'destination_port': 22}]:
            self.assertEqual(evaluate_flow([self.rule], dict(self.flow, **patch))['decision'], 'deny')

    def test_first_match_order_changes_result(self):
        deny = dict(self.rule, id='DENY', action='deny')
        self.assertEqual(evaluate_flow([deny, self.rule], self.flow)['decision'], 'deny')
        self.assertEqual(evaluate_flow([self.rule, deny], self.flow)['decision'], 'allow')

    def test_bad_inputs_and_duplicate_rules_rejected(self):
        for patch in [{'destination_port': 0}, {'destination_port': True}, {'source': 'bad'}, {'protocol': 'icmp'}]:
            with self.assertRaises(ValueError): evaluate_flow([self.rule], dict(self.flow, **patch))
        with self.assertRaises(ValueError): evaluate_flow([self.rule, self.rule], self.flow)

    def test_no_mutation_and_example_decisions(self):
        before = deepcopy((self.rule, self.flow))
        evaluate_flow([self.rule], self.flow)
        self.assertEqual((self.rule, self.flow), before)
        self.assertEqual([f['decision'] for f in demo()['network']], ['deny', 'allow', 'allow', 'deny'])


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = {'example.txt': b'Fictional evidence'}
        self.record = {'control_id': 'LAB-1', 'owner': 'Fictional owner', 'review_status': 'reviewed',
                       'expected_scope': 'Example system', 'evidence_scope': 'Example system', 'collected_on': '2026-11-09',
                       'max_age_days': 30, 'artifact': 'example.txt', 'sha256': hashlib.sha256(self.data['example.txt']).hexdigest()}

    def gaps(self, **patch):
        return assess_evidence([dict(self.record, **patch)], self.data, '2026-11-09')[0]['gaps']

    def test_complete_evidence_is_not_called_compliance(self):
        result = assess_evidence([self.record], self.data, '2026-11-09')[0]
        self.assertEqual(result['gaps'], [])
        self.assertEqual(result['status'], 'Ready for manual control assessment')

    def test_missing_owner_review_and_scope_are_distinct_gaps(self):
        self.assertEqual(self.gaps(owner='', review_status='pending', evidence_scope='wrong'),
                         ['OWNER_MISSING', 'REVIEW_NOT_RECORDED', 'SCOPE_MISMATCH'])

    def test_missing_and_changed_artifacts_detected(self):
        self.assertEqual(self.gaps(artifact='missing.txt'), ['ARTIFACT_MISSING'])
        self.data['example.txt'] += b' altered'
        self.assertEqual(self.gaps(), ['HASH_MISMATCH'])

    def test_date_boundaries_and_bad_dates(self):
        self.assertEqual(self.gaps(collected_on='2026-10-10'), [])
        self.assertEqual(self.gaps(collected_on='2026-10-09'), ['STALE_UNDER_LAB_CRITERION'])
        self.assertEqual(self.gaps(collected_on='2026-11-10'), ['FUTURE_COLLECTION_DATE'])
        self.assertEqual(self.gaps(collected_on='unknown'), ['INVALID_COLLECTION_DATE'])

    def test_duplicate_controls_rejected(self):
        with self.assertRaises(ValueError): assess_evidence([self.record, self.record], self.data, '2026-11-09')


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.records = {'EXAMPLE-1': {'owner': 'U-001', 'content': 'Fictional note'}}
        self.roles = {'U-001': 'reader', 'U-002': 'reader', 'U-010': 'review_admin'}

    def test_demonstrates_horizontal_authorization_bug_and_fix(self):
        self.assertEqual(get_record_vulnerable('U-002', 'EXAMPLE-1', self.records, self.roles)[0], 200)
        self.assertEqual(get_record_authorized('U-002', 'EXAMPLE-1', self.records, self.roles), (404, None))

    def test_owner_and_authorized_reviewer_can_read(self):
        for principal in ['U-001', 'U-010']:
            self.assertEqual(get_record_authorized(principal, 'EXAMPLE-1', self.records, self.roles)[0], 200)

    def test_unknown_principal_and_missing_object(self):
        self.assertEqual(get_record_authorized('UNKNOWN', 'EXAMPLE-1', self.records, self.roles), (401, None))
        self.assertEqual(get_record_authorized('U-001', 'missing', self.records, self.roles), (404, None))

    def test_returned_object_does_not_mutate_source(self):
        _, result = get_record_authorized('U-001', 'EXAMPLE-1', self.records, self.roles)
        result['content'] = 'Changed local copy'
        self.assertEqual(self.records['EXAMPLE-1']['content'], 'Fictional note')


if __name__ == '__main__': unittest.main()
