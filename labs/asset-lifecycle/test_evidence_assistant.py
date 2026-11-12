import unittest
from evidence_assistant import review, sample_report


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = sample_report()

    def test_categories(self):
        for question, topic in [("Which devices are patched?", "installed"),
                                ("missing offline", "no target evidence"),
                                ("outdated", "stale evidence"),
                                ("contradictory", "conflicting reports"),
                                ("queued", "pending"), ("failure", "failed")]:
            with self.subTest(topic=topic):
                result = review(question, self.report)
                self.assertEqual(result["matched_topic"], topic)
                expected = [r for r in self.report["devices"] if r["result"] == topic]
                self.assertEqual(result["evidence"], expected)
                self.assertEqual(result["matched_count"], len(expected))

    def test_abstention(self):
        for query in ["", "the", "rotate database passwords", "failed pending"]:
            self.assertEqual(review(query, self.report), {"status": "insufficient evidence"})
