import unittest
from trust_analysis.core import experience_group, users_only_summary


class ReviewCases(unittest.TestCase):
    def test_experience_boundaries(self):
        for value, expected in [
            ("1", "0-1 years"),
            ("2", "2 years"),
            ("20", "11-20 years"),
            ("21", "21+ years"),
        ]:
            self.assertEqual(experience_group(value), expected)

    def test_users_only_excludes_nonusers(self):
        rows = [
            {
                "year": 2025,
                "using_ai": using,
                "trust": label,
                "count": count,
                "denominator": total,
            }
            for using, total, counts in [(True, 10, [4, 2, 4]), (False, 90, [0, 0, 90])]
            for label, count in zip(["positive", "neutral", "negative"], counts)
        ]
        result = users_only_summary(rows)[0]
        self.assertEqual(result["trust_n"], 10)
        self.assertEqual(result["positive_trust_pct"], 40)
        rows[0]["count"] = 5
        with self.assertRaises(ValueError):
            users_only_summary(rows)
