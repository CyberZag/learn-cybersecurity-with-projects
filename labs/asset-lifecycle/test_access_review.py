from copy import deepcopy
import json
from pathlib import Path
import unittest

from access_review import review
from asset_lab import run_demo


class AccessReviewTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).parent
        self.inventory = json.loads((base/'sample_data.json').read_text(encoding='utf-8-sig'))
        self.scope = json.loads((base/'access_review_data.json').read_text(encoding='utf-8-sig'))

    def report(self):
        return review(self.inventory, self.scope, '2026-11-09')

    def codes(self, index):
        return {f['code'] for f in self.report()['accounts'][index]['findings']}

    def test_expected_review_candidates_and_preserved_inputs(self):
        original = deepcopy((self.inventory, self.scope))
        self.assertEqual(self.report()['finding_counts'], {'EXPIRED_EXCEPTION': 1, 'LEAVER_ACCESS_REVIEW': 1,
            'ROLE_DEVIATION_REVIEW': 2, 'SEPARATION_OF_DUTIES_REVIEW': 1, 'UNKNOWN_PERMISSION': 1,
            'UNKNOWN_ROLE': 1, 'UNKNOWN_SUBJECT': 1})
        self.assertEqual((self.inventory, self.scope), original)
        self.assertEqual(self.report(), self.report())

    def test_unknown_role_is_not_assumed_to_have_zero_entitlement(self):
        self.assertEqual(self.codes(3), {'UNKNOWN_ROLE'})

    def test_unknown_permission_is_data_quality_finding(self):
        self.assertEqual(self.codes(4), {'UNKNOWN_PERMISSION'})

    def test_equipment_recovery_does_not_remove_access_finding(self):
        self.inventory, _ = run_demo(self.inventory)
        self.assertIn('LEAVER_ACCESS_REVIEW', self.codes(2))

    def test_disabled_leaver_with_assignments_still_requires_review(self):
        self.scope['accounts'][2]['enabled'] = False
        self.assertIn('LEAVER_ACCESS_REVIEW', self.codes(2))
        self.scope['accounts'][2]['permissions'] = []
        self.assertNotIn('LEAVER_ACCESS_REVIEW', self.codes(2))

    def test_exception_valid_through_expiry_then_requires_review(self):
        self.scope['accounts'][5]['exceptions'][0]['expires_on'] = '2026-11-09'
        self.assertEqual(self.codes(5), set())
        result = review(self.inventory, self.scope, '2026-11-10')
        self.assertEqual({f['code'] for f in result['accounts'][5]['findings']}, {'EXPIRED_EXCEPTION', 'ROLE_DEVIATION_REVIEW'})

    def test_exception_does_not_hide_conflicting_permissions(self):
        self.scope['accounts'][0]['exceptions'] = [{'permission': 'invoice.approve', 'reviewer_id': 'U-010',
            'expires_on': '2026-12-01', 'evidence': 'Fictional exception'}]
        self.assertEqual(self.codes(0), {'SEPARATION_OF_DUTIES_REVIEW'})

    def test_self_inactive_missing_or_malformed_exception_is_not_accepted(self):
        for change in [{'reviewer_id': 'U-006'}, {'reviewer_id': 'U-003'}, {'reviewer_id': 'UNKNOWN'},
                       {'evidence': ''}, {'expires_on': 'not-a-date'}, {'reviewer_id': []}]:
            with self.subTest(change=change):
                original = deepcopy(self.scope)
                self.scope['accounts'][5]['exceptions'][0].update(change)
                self.assertEqual(self.codes(5), {'INVALID_EXCEPTION', 'ROLE_DEVIATION_REVIEW'})
                self.scope = original

    def test_unknown_subject_is_never_silently_approved(self):
        self.assertEqual(self.codes(7), {'UNKNOWN_SUBJECT'})

    def test_duplicate_account_rejected(self):
        self.scope['accounts'].append(deepcopy(self.scope['accounts'][0]))
        with self.assertRaisesRegex(ValueError, 'unique'): self.report()

    def test_bad_policy_rejected(self):
        self.scope['roles']['clerk'].append('not.in.catalogue')
        with self.assertRaisesRegex(ValueError, 'unknown permission'): self.report()

    def test_explicit_synthetic_markers_required(self):
        for value in [False, None, 1, 'true']:
            self.scope['synthetic'] = value
            with self.assertRaisesRegex(ValueError, 'synthetic'): self.report()

    def test_empty_scope_rejected(self):
        self.scope['accounts'] = []
        with self.assertRaisesRegex(ValueError, 'Nonempty'): self.report()

    def test_no_finding_has_limited_scope_wording(self):
        row = self.report()['accounts'][1]
        self.assertEqual(row['status'], 'No finding under these limited checks')
        self.assertIn('not complete', self.report()['scope']['coverage'])


if __name__ == '__main__': unittest.main()
