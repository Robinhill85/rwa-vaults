import importlib.util
import unittest
spec = importlib.util.spec_from_file_location("cmc", "registry/cmc_rwa.py")
cmc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmc)

class TotalsTest(unittest.TestCase):
    def test_zero_is_a_value(self):
        self.assertEqual(cmc.sum_complete([{"cap": 0}], "cap"), 0)
    def test_missing_contribution_does_not_become_a_total(self):
        self.assertIsNone(cmc.sum_complete([{"cap": 50}, {"cap": None}], "cap"))
        self.assertIsNone(cmc.sum_complete([], "cap"))
    def test_complete_total(self):
        self.assertEqual(cmc.sum_complete([{"cap": 50}, {"cap": 25}], "cap"), 75)

if __name__ == "__main__":
    unittest.main()
