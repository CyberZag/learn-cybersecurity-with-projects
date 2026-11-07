import json
from copy import deepcopy
from pathlib import Path
import unittest
from asset_lab import apply_ticket, findings, run_demo, validate

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((Path(__file__).parent/'sample_data.json').read_text())
    def test_fixture_outcomes_and_input_unchanged(self):
        original=deepcopy(self.data)
        final,report=run_demo(self.data)
        self.assertEqual(self.data,original)
        self.assertEqual(len(report['findings_before']),1)
        self.assertEqual(report['findings_after'],[])
        self.assertEqual([x['decision'] for x in report['audit']],['applied_in_simulation','blocked','applied_in_simulation','blocked','blocked'])
        self.assertEqual(next(a for a in final['assets'] if a['asset_id']=='CI-003')['status'],'repair')
    def test_unapproved_does_not_mutate(self):
        state,event=apply_ticket(self.data,'T-002','test-time')
        self.assertEqual(event['decision'],'blocked'); self.assertEqual(state,self.data)
    def test_self_approval_refused(self):
        self.data['tickets'][0]['approved_by']='U-001'
        state,event=apply_ticket(self.data,'T-001','test-time')
        self.assertIn('own change',event['reason']); self.assertEqual(state,self.data)
    def test_leaver_recipient_refused(self):
        self.data['tickets'][0]['to_user']='U-003'
        state,event=apply_ticket(self.data,'T-001','test-time')
        self.assertIn('active recipient',event['reason']); self.assertEqual(state,self.data)
    def test_closed_ticket_cannot_replay(self):
        state,_=apply_ticket(self.data,'T-001','test-time')
        again,event=apply_ticket(state,'T-001','test-time')
        self.assertIn('replay',event['reason']); self.assertEqual(state,again)
    def test_stale_request_refused(self):
        self.data['tickets'][0]['expected_status']='active'
        state,event=apply_ticket(self.data,'T-001','test-time')
        self.assertIn('stale',event['reason']); self.assertEqual(state,self.data)
    def test_retirement_requires_sanitization_evidence(self):
        state,event=apply_ticket(self.data,'T-004','test-time')
        self.assertIn('Sanitization',event['reason']); self.assertEqual(state,self.data)
        self.data['tickets'][3]['sanitization_evidence']='SYNTHETIC wipe-review record EXAMPLE-04'
        state,event=apply_ticket(self.data,'T-004','test-time')
        self.assertEqual(event['decision'],'applied_in_simulation')
        self.assertEqual(state['assets'][3]['status'],'retired')
    def test_duplicate_and_dangling_identifiers_rejected(self):
        for corrupt in ['duplicate','dangling']:
            data=deepcopy(self.data)
            if corrupt=='duplicate': data['assets'].append(deepcopy(data['assets'][0]))
            else: data['tickets'][0]['asset_id']='DOES-NOT-EXIST'
            with self.assertRaises(ValueError): validate(data)
    def test_inactive_approver_and_missing_evidence_refused(self):
        for change in [{'approved_by':'U-003'},{'evidence':''}]:
            data=deepcopy(self.data); data['tickets'][0].update(change)
            state,event=apply_ticket(data,'T-001','test-time')
            self.assertEqual(event['decision'],'blocked'); self.assertEqual(state,data)
    def test_illegal_asset_state_rejected(self):
        self.data['assets'][0]['status']='retired'
        self.data['assets'][0]['assigned_to']='U-001'
        with self.assertRaises(ValueError): validate(self.data)

if __name__=='__main__': unittest.main(verbosity=2)
