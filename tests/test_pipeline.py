import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from trust_analysis.__main__ import run
from trust_analysis.core import TRUST_COLUMN


class EndToEnd(unittest.TestCase):
    def test_schema_alignment_outputs_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for year in [2023, 2024, 2025]:
                directory = root / str(year)
                directory.mkdir()
                yes = "Yes" if year < 2025 else "Yes, I use AI tools weekly"
                pd.DataFrame(
                    {
                        "ResponseId": [1, 2, 3],
                        "AISelect": [yes, yes, "No, and I don't plan to"],
                        TRUST_COLUMN[year]: [
                            "Highly trust",
                            "Neither trust nor distrust",
                            "Somewhat distrust",
                        ],
                        "AISent": ["Very favorable", "Unsure", "Unfavorable"],
                    }
                ).to_csv(directory / "survey_results_public.csv", index=False)
                pd.DataFrame(
                    {
                        "qname": [TRUST_COLUMN[year]],
                        "question": ["How much do you trust the accuracy of output?"],
                    }
                ).to_csv(directory / "survey_results_schema.csv", index=False)
            out = root / "new"
            run(root, out)
            summary = pd.read_csv(out / "annual_summary.csv")
            self.assertEqual(summary.negative_trust.tolist(), [1, 1, 1])
            self.assertEqual(summary.neutral_trust.tolist(), [1, 1, 1])
            manifest = (out / "provenance.json").read_text()
            self.assertNotIn(tmp, manifest)
            self.assertEqual(
                [s["trust_column"] for s in json.loads(manifest)["sources"]],
                ["AIBen", "AIAcc", "AIAcc"],
            )
            self.assertIn("<svg", (out / "adoption-and-trust.svg").read_text())
            before = (out / "annual_summary.csv").read_bytes()
            with self.assertRaises(ValueError):
                run(root, out)
            self.assertEqual(before, (out / "annual_summary.csv").read_bytes())
