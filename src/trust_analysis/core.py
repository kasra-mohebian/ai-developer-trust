"""Explicit survey semantics and respondent-aligned descriptive statistics."""

from __future__ import annotations
import math
import numpy as np
import pandas as pd

TRUST_COLUMN = {2023: "AIBen", 2024: "AIAcc", 2025: "AIAcc"}
TRUST = {
    "Highly distrust": 1,
    "Somewhat distrust": 2,
    "Neither trust nor distrust": 3,
    "Somewhat trust": 4,
    "Highly trust": 5,
}
SENTIMENT = {
    "Very unfavorable": 1,
    "Unfavorable": 2,
    "Indifferent": 3,
    "Favorable": 4,
    "Very favorable": 5,
}
ADOPTION = {
    2023: {
        "Yes": True,
        "No, and I don't plan to": False,
        "No, but I plan to soon": False,
    },
    2024: {
        "Yes": True,
        "No, and I don't plan to": False,
        "No, but I plan to soon": False,
    },
    2025: {
        "Yes, I use AI tools daily": True,
        "Yes, I use AI tools weekly": True,
        "Yes, I use AI tools monthly or infrequently": True,
        "No, and I don't plan to": False,
        "No, but I plan to soon": False,
    },
}


def wilson(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    """Binomial interval for a sample proportion; does not remove selection bias."""
    if total < 0 or not 0 <= successes <= total:
        raise ValueError("Require 0 <= successes <= total")
    if total == 0:
        return float("nan"), float("nan")
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = (
        z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    )
    return (
        0.0 if successes == 0 else 100 * max(0, center - half),
        100.0 if successes == total else 100 * min(1, center + half),
    )


def percentage(count: int, total: int) -> float:
    return 100 * count / total if total else float("nan")


def prepare(frame: pd.DataFrame, year: int) -> pd.DataFrame:
    """Select adoption respondents, retaining row identity through every analysis."""
    required = {"ResponseId", "AISelect", "AISent", TRUST_COLUMN[year]}
    missing = required - set(frame)
    if missing:
        raise ValueError(f"{year}: missing required columns {sorted(missing)}")
    if frame["ResponseId"].isna().any() or frame["ResponseId"].duplicated().any():
        raise ValueError(
            f"{year}: respondent identifiers must be present and unique within year"
        )
    d = frame.loc[frame.AISelect.notna()].copy()
    if d.empty:
        raise ValueError(f"{year}: no eligible adoption answers")
    unknown = set(d.AISelect.unique()) - set(ADOPTION[year])
    if unknown:
        raise ValueError(f"{year}: unknown adoption categories: {sorted(unknown)}")
    d["using_ai"] = d.AISelect.map(ADOPTION[year]).astype(bool)
    raw_trust = d[TRUST_COLUMN[year]]
    unknown_trust = set(raw_trust.dropna().unique()) - set(TRUST)
    if unknown_trust:
        raise ValueError(f"{year}: unknown trust categories: {sorted(unknown_trust)}")
    unknown_sentiment = set(d.AISent.dropna().unique()) - set(SENTIMENT) - {"Unsure"}
    if unknown_sentiment:
        raise ValueError(
            f"{year}: unknown sentiment categories: {sorted(unknown_sentiment)}"
        )
    d["trust_score"] = raw_trust.map(TRUST)
    d["sentiment_score"] = d.AISent.map(
        SENTIMENT
    )  # Unsure remains missing, not neutral.
    d["year"] = year
    return d


def summarize(
    frame: pd.DataFrame, year: int
) -> tuple[dict, list[dict], dict, list[dict]]:
    d = prepare(frame, year)
    t = d.loc[d.trust_score.notna()]
    positive, negative, neutral = (
        int((t.trust_score >= 4).sum()),
        int((t.trust_score <= 2).sum()),
        int((t.trust_score == 3).sum()),
    )
    n, using = len(d), int(d.using_ai.sum())
    low, high = wilson(using, n)
    summary = {
        "year": year,
        "raw_rows": len(frame),
        "adoption_n": n,
        "using_ai": using,
        "not_using_ai": n - using,
        "adoption_pct": percentage(using, n),
        "adoption_wilson_low": low,
        "adoption_wilson_high": high,
        "trust_n": len(t),
        "positive_trust": positive,
        "negative_trust": negative,
        "neutral_trust": neutral,
        "positive_trust_pct": percentage(positive, len(t)),
        "negative_trust_pct": percentage(negative, len(t)),
        "neutral_trust_pct": percentage(neutral, len(t)),
        "sentiment_unsure_n": int(d.AISent.eq("Unsure").sum()),
    }
    summary["adoption_minus_positive_trust_pp"] = (
        summary["adoption_pct"] - summary["positive_trust_pct"]
    )
    distribution = [
        {
            "year": year,
            "category": label,
            "count": int(t.trust_score.eq(score).sum()),
            "denominator": len(t),
            "pct": percentage(int(t.trust_score.eq(score).sum()), len(t)),
        }
        for label, score in TRUST.items()
    ]
    paired = d[["trust_score", "sentiment_score"]].dropna()
    rho = (
        paired.trust_score.rank().corr(paired.sentiment_score.rank())
        if len(paired) > 1
        else float("nan")
    )
    correlation = {"year": year, "pair_n": len(paired), "spearman_rho": float(rho)}
    # The same respondent supplies both adoption and trust; no positional join.
    cross = []
    for using_value in [False, True]:
        group = t[t.using_ai.eq(using_value)]
        for label, condition in [
            ("positive", group.trust_score.ge(4)),
            ("neutral", group.trust_score.eq(3)),
            ("negative", group.trust_score.le(2)),
        ]:
            count = int(condition.sum())
            cross.append(
                {
                    "year": year,
                    "using_ai": using_value,
                    "trust": label,
                    "count": count,
                    "denominator": len(group),
                    "within_adoption_group_pct": percentage(count, len(group)),
                }
            )
    return summary, distribution, correlation, cross


def grouped_trust(
    d: pd.DataFrame, column: str, year: int, minimum: int = 100
) -> list[dict]:
    if column not in d:
        return []
    records = []
    for label, group in d.dropna(subset=[column]).groupby(column, sort=True):
        if len(group) < minimum:
            continue
        t = group[group.trust_score.notna()]
        records.append(
            {
                "year": year,
                "group": str(label),
                "adoption_n": len(group),
                "adoption_pct": percentage(int(group.using_ai.sum()), len(group)),
                "trust_n": len(t),
                "positive_trust_pct": percentage(
                    int(t.trust_score.ge(4).sum()), len(t)
                ),
            }
        )
    return records


def experience_group(value):
    if pd.isna(value):
        return None
    if value == "Less than 1 year":
        number = 0
    elif value == "More than 50 years":
        number = 51
    else:
        try:
            number = float(value)
        except (ValueError, TypeError):
            return None
    if number < 0:
        return None
    for maximum, label in [
        (1, "0-1 years"),
        (2, "2 years"),
        (5, "3-5 years"),
        (10, "6-10 years"),
        (20, "11-20 years"),
    ]:
        if number <= maximum:
            return label
    return "21+ years"


def cramers_v(table) -> float:
    obs = np.asarray(table, dtype=float)
    if (
        obs.ndim != 2
        or min(obs.shape) < 2
        or (obs < 0).any()
        or not np.isfinite(obs).all()
    ):
        raise ValueError(
            "A finite nonnegative contingency table with at least two rows/columns is required"
        )
    total = obs.sum()
    if total == 0 or (obs.sum(axis=0) == 0).any() or (obs.sum(axis=1) == 0).any():
        return float("nan")
    expected = np.outer(obs.sum(axis=1), obs.sum(axis=0)) / total
    chi2 = ((obs - expected) ** 2 / expected).sum()
    return float(np.sqrt(chi2 / (total * min(obs.shape[0] - 1, obs.shape[1] - 1))))


def users_only_summary(joint):
    """Trust among current AI users with a valid trust answer, by year."""
    records = []
    for year in sorted({row["year"] for row in joint}):
        group = {
            row["trust"]: row
            for row in joint
            if row["year"] == year and row["using_ai"]
        }
        if set(group) != {"positive", "neutral", "negative"}:
            raise ValueError(f"{year}: incomplete users-only trust categories")
        denominators = {row["denominator"] for row in group.values()}
        if len(denominators) != 1:
            raise ValueError(f"{year}: inconsistent users-only denominators")
        total = denominators.pop()
        if sum(row["count"] for row in group.values()) != total:
            raise ValueError(f"{year}: users-only counts do not sum to denominator")
        result = {"year": year, "trust_n": total}
        for category, row in group.items():
            result[category + "_trust"] = row["count"]
            result[category + "_trust_pct"] = percentage(row["count"], total)
        records.append(result)
    return records
