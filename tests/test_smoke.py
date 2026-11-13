"""Kleiner Smoke-Test mit synthetischen Beispieldaten (keine Original-KBA-/AMS-Daten)."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyse_kfz import joined_data, weighted_mean


class SyntheticJoinTest(unittest.TestCase):
    def test_join_and_weighting(self):
        kba = pd.DataFrame({
            "HSN": ["0001", "0001", "0002"], "TSN": ["AAA", "AAB", "BBB"],
            "Bestand": [10, 30, 20],
        })
        ams = pd.DataFrame({
            "HSN": ["0001", "0001"], "TSN": ["AAA", "AAB"],
            "HP": [12, 18],
        })
        merged = joined_data(kba, ams)
        self.assertEqual(len(merged), 2)
        self.assertEqual(int(merged["Bestand"].sum()), 40)
        self.assertAlmostEqual(weighted_mean(merged["HP"], merged["Bestand"]), 16.5)


if __name__ == "__main__":
    unittest.main()
