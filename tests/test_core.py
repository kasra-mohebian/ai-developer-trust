"""Synthetic edge cases; no real respondent records are included."""

import unittest
import numpy as np
import pandas as pd
from trust_analysis.core import prepare, summarize, cramers_v, wilson, experience_group


class SurveySemantics(unittest.TestCase):
    def fixture(self, year=2024):
        return pd.DataFrame(
            {
                "ResponseId": [1, 2, 3, 4],
                "AISelect": ["Yes", "Yes", "No, and I don't plan to", None],
                "AIAcc": [
                    "Highly trust",
                    "Neither trust nor distrust",
                    "Somewhat distrust",
                    "Highly trust",
                ],
                "AISent": ["Very favorable", "Unsure", "Unfavorable", "Very favorable"],
            }
        )

    def test_neutral_is_not_negative(self):
        summary, _, corr, _ = summarize(self.fixture(), 2024)
        self.assertEqual(summary["positive_trust"], 1)
        self.assertEqual(summary["negative_trust"], 1)
        self.assertEqual(summary["neutral_trust"], 1)
        self.assertEqual(summary["trust_n"], 3)
        self.assertEqual(corr["pair_n"], 2)

    def test_2023_column_semantics(self):
        d = self.fixture().rename(columns={"AIAcc": "AIBen"})
        d["AIAcc"] = ["Increase productivity"] * 4
        self.assertEqual(summarize(d, 2023)[0]["positive_trust"], 1)

    def test_pairing_survives_row_order_and_missingness(self):
        a = summarize(self.fixture(), 2024)[2]
        b = summarize(self.fixture().iloc[[2, 0, 3, 1]], 2024)[2]
        self.assertAlmostEqual(a["spearman_rho"], b["spearman_rho"])
        self.assertAlmostEqual(a["spearman_rho"], 1.0)

    def test_unknown_category_fails(self):
        d = self.fixture()
        d.loc[0, "AIAcc"] = "Maybe"
        with self.assertRaises(ValueError):
            prepare(d, 2024)

    def test_duplicate_identifier_fails(self):
        d = self.fixture()
        d.loc[1, "ResponseId"] = 1
        with self.assertRaises(ValueError):
            prepare(d, 2024)

    def test_2025_frequencies_are_current_use(self):
        d = self.fixture().iloc[:3].copy()
        d["AISelect"] = [
            "Yes, I use AI tools daily",
            "Yes, I use AI tools monthly or infrequently",
            "No, but I plan to soon",
        ]
        self.assertEqual(summarize(d, 2025)[0]["using_ai"], 2)

    def test_cramers_minimum_dimension(self):
        value = cramers_v([[39042, 48931], [37662, 23245], [26469, 7251]])
        self.assertAlmostEqual(value, 0.26270757007152645)

    def test_intervals_and_experience_boundaries(self):
        lo, hi = wilson(0, 100)
        self.assertEqual(lo, 0)
        self.assertGreater(hi, 0)
        self.assertTrue(np.isnan(wilson(0, 0)[0]))
        self.assertEqual(experience_group("Less than 1 year"), "0-1 years")
        self.assertEqual(experience_group("More than 50 years"), "21+ years")
        self.assertIsNone(experience_group("unknown"))


if __name__ == "__main__":
    unittest.main()
