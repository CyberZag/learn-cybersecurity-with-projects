from copy import deepcopy
import unittest
from control_workpaper import build_workpapers, fixture, render


class WorkpaperTests(unittest.TestCase):
    def test_three_cases_have_distinct_evidence_outcomes(self):
        report = build_workpapers(*fixture(), '2026-11-10')
        self.assertEqual(report['summary'], {'total': 3, 'evidence_requests': 2, 'ready_for_manual_testing': 1})
        self.assertEqual(report['workpapers'][1]['gaps'], ['OWNER_MISSING', 'REVIEW_NOT_RECORDED', 'SCOPE_MISMATCH'])
        self.assertEqual(report['workpapers'][2]['gaps'], ['ARTIFACT_MISSING'])

    def test_matching_metadata_does_not_become_effectiveness_or_risk_score(self):
        for p in build_workpapers(*fixture(), '2026-11-10')['workpapers']:
            self.assertEqual(p['manual_effectiveness_assessment'], 'Not performed')
            self.assertIsNone(p['risk_rating'])

    def test_changed_evidence_blocks_formerly_ready_workpaper(self):
        records, artifacts, metadata = fixture()
        artifacts['inventory.txt'] += b'changed'
        p = build_workpapers(records, artifacts, metadata, '2026-11-10')['workpapers'][0]
        self.assertIn('HASH_MISMATCH', p['gaps'])
        self.assertEqual(p['disposition'], 'Request evidence')

    def test_fixing_one_gap_does_not_hide_remaining_access_gaps(self):
        records, artifacts, metadata = fixture()
        records[1]['owner'] = 'Fictional reviewer'
        p = build_workpapers(records, artifacts, metadata, '2026-11-10')['workpapers'][1]
        self.assertEqual(p['gaps'], ['REVIEW_NOT_RECORDED', 'SCOPE_MISMATCH'])
        self.assertEqual(p['disposition'], 'Request evidence')

    def test_retest_requires_all_manifest_gaps_resolved(self):
        records, artifacts, metadata = fixture()
        records[1].update(owner='Fictional reviewer', review_status='reviewed', evidence_scope='All eight fictional accounts')
        p = build_workpapers(records, artifacts, metadata, '2026-11-10')['workpapers'][1]
        self.assertEqual(p['disposition'], 'Proceed to manual testing')
        self.assertEqual(p['manual_effectiveness_assessment'], 'Not performed')

    def test_missing_or_unmatched_context_rejected(self):
        records, artifacts, metadata = fixture()
        metadata['LAB-ACCESS']['procedure'] = ''
        with self.assertRaises(ValueError): build_workpapers(records, artifacts, metadata, '2026-11-10')
        del metadata['LAB-ACCESS']
        with self.assertRaises(ValueError): build_workpapers(records, artifacts, metadata, '2026-11-10')

    def test_inputs_preserved_and_render_contains_all_findings(self):
        values = fixture(); before = deepcopy(values)
        report = build_workpapers(*values, '2026-11-10')
        self.assertEqual(values, before)
        text = render(report)
        for p in report['workpapers']:
            self.assertIn(p['control_id'], text)
            for gap in p['gaps']: self.assertIn(gap, text)
        self.assertIn('learner reproduction remains unverified', text)


if __name__ == '__main__': unittest.main()
