from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

from support_portal import make_report, render_html


class Elements(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        self.ids.extend(v for k,v in attrs if k=='id')


class SupportPortalTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((Path(__file__).parent/'sample_data.json').read_text(encoding='utf-8-sig'))

    def test_decisions_are_grounded_and_input_unchanged(self):
        before=deepcopy(self.data); report=make_report(self.data)
        self.assertEqual(self.data,before)
        self.assertEqual(report['counts'],{'Simulated change complete':2,'Held for review':3})
        self.assertEqual([r['ticket_id'] for r in report['tickets']],['T-001','T-002','T-003','T-004','T-005'])

    def test_blocked_requests_preserve_state_and_do_not_claim_resolution(self):
        for row in make_report(self.data)['tickets']:
            if row['status']=='Held for review':
                self.assertEqual(row['before'],row['after'])
                self.assertIn('No inventory change',row['customer_update_draft'])
                self.assertIn('Unassigned',row['priority'])
                self.assertIn('no service-level promise',row['follow_up'])

    def test_unmarked_data_is_rejected(self):
        for bad in [False,None,'true',1]:
            with self.subTest(bad=bad):
                self.data['synthetic']=bad
                with self.assertRaises(ValueError):make_report(self.data)

    def test_existing_validation_rejects_duplicate_requests(self):
        self.data['tickets'].append(deepcopy(self.data['tickets'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate ticket_id'):make_report(self.data)

    def test_html_is_script_free_and_escapes_dataset_text(self):
        report=make_report(self.data)
        report['tickets'][0]['ticket_id']='<script>alert("test")</script>'
        report['tickets'][0]['reason']='<img src=x onerror=alert(1)>'
        html=render_html(report); parser=Elements();parser.feed(html)
        self.assertNotIn('script',parser.tags);self.assertNotIn('img',parser.tags)
        self.assertNotIn('form',parser.tags);self.assertNotIn('input',parser.tags)
        self.assertIn('&lt;script&gt;',html);self.assertIn('&lt;img',html)
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertEqual(parser.tags.count('article'),5)

    def test_repaired_fixture_changes_only_expected_outcome(self):
        self.data['tickets'][1]['approved_by']=self.data['tickets'][0]['approved_by']
        # Missing approval is fixed; any additional blocker must still be surfaced.
        report=make_report(self.data)
        self.assertNotIn('Active approver and known requester required',report['tickets'][1]['reason'])
        for row in report['tickets'][3:]:self.assertEqual(row['status'],'Held for review')


if __name__=='__main__':unittest.main()
