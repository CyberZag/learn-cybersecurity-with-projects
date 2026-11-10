import json
from copy import deepcopy
import unittest
from patch_coverage import HERE, reconcile


class PatchCoverageTests(unittest.TestCase):
    def setUp(self):
        self.inventory = json.loads((HERE / "sample_data.json").read_text())
        self.snapshot = json.loads((HERE / "patch_snapshot.json").read_text())

    def test_inventory_owns_denominator(self):
        result = reconcile(self.inventory, self.snapshot)
        self.assertEqual((result["verified_installed"], result["active_devices"]), (3, 18))
        self.assertEqual(sum(result["by_state"].values()), 18)
        self.assertEqual(result["by_state"]["no target evidence"], 11)

    def test_order_and_repeat_delivery_do_not_change_decisions(self):
        before = reconcile(self.inventory, self.snapshot)
        self.snapshot["reports"].reverse()
        self.snapshot["reports"].extend(deepcopy(self.snapshot["reports"]))
        self.assertEqual(reconcile(self.inventory, self.snapshot), before)

    def test_exceptions_stay_outside_verified_population(self):
        result = reconcile(self.inventory, self.snapshot)
        self.assertEqual({x["asset_id"] for x in result["exceptions"]}, {"CI-001","CI-009","CI-999"})
        decisions = {x["asset_id"]:x["result"] for x in result["devices"]}
        self.assertEqual(decisions["CI-009"], "no target evidence")
        self.assertEqual(decisions["CI-007"], "no target evidence")
        self.assertEqual(decisions["CI-006"], "conflicting reports")

    def test_freshness_boundary_and_latest_report(self):
        decisions = {x["asset_id"]:x["result"] for x in reconcile(self.inventory,self.snapshot)["devices"]}
        self.assertEqual(decisions["CI-011"], "installed")
        self.assertEqual(decisions["CI-008"], "installed")
        self.assertEqual(decisions["CI-005"], "stale evidence")
        self.snapshot["as_of"] = "2026-11-10T17:00:01Z"
        rows = reconcile(self.inventory, self.snapshot)["devices"]
        self.assertEqual(next(x["result"] for x in rows if x["asset_id"]=="CI-011"), "stale evidence")

    def test_invalid_cutoffs_are_rejected(self):
        for key, value in [("as_of","2026-11-10T17:00:00"), ("freshness_hours",False), ("target_update","")]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                reconcile(self.inventory, {**self.snapshot, key:value})

    def test_missing_feed_keeps_the_full_inventory_visible(self):
        result = reconcile(self.inventory, {**self.snapshot, "reports":[]})
        self.assertEqual(result["by_state"], {"no target evidence":18})
