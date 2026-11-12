import unittest
from grc_assistant import answer, register, workpapers


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.papers = workpapers("2026-11-10")

    def ask(self, proposal):
        return answer("Who reviews permissions?", self.papers, "test",
                      route=lambda *args: proposal)

    def test_register(self):
        rows = register(self.papers)
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(r["decision"] == "Request evidence" for r in rows), 2)

    def test_missing_owner_preserved(self):
        row = self.ask({"case": "LAB-ACCESS"})["candidate"]
        self.assertIsNone(row["owner"])
        self.assertEqual(row["nist_csf_2"], "PR.AA-05")
        self.assertTrue(row["gaps"])

    def test_unknown(self):
        self.assertEqual(self.ask({"case": "UNKNOWN"})["state"], "unmapped")

    def test_reject_model_claims(self):
        for proposal in [{"case": "LAB-ACCESS", "certified": True},
                         {"case": "MADE-UP"}, {"case": []}, "LAB-ACCESS"]:
            with self.subTest(proposal=proposal), self.assertRaises(ValueError):
                self.ask(proposal)

    def test_older_evidence(self):
        then = register(self.papers)
        later = register(workpapers("2027-01-10"))
        self.assertGreater(len(later[0]["gaps"]), len(then[0]["gaps"]))
