"""CLI: python -m trust_analysis --data-root DATA --output NEW_DIRECTORY."""

from __future__ import annotations
import argparse
import hashlib
import json
import math
import warnings
from pathlib import Path
from xml.sax.saxutils import escape
import numpy as np
import pandas as pd
from .core import (
    TRUST_COLUMN,
    prepare,
    summarize,
    grouped_trust,
    experience_group,
    cramers_v,
    users_only_summary,
)


def locate(root: Path, year: int, name: str) -> Path:
    candidates = [
        root / str(year) / name,
        root / f"stack-overflow-developer-survey-{year}" / name,
    ]
    found = [p for p in candidates if p.is_file()]
    if len(found) != 1:
        raise ValueError(
            f"Expected exactly one {year}/{name} input; found {len(found)}"
        )
    return found[0]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_schema(path: Path, year: int) -> None:
    schema = pd.read_csv(path, encoding="utf-8-sig")
    if not {"qname", "question"}.issubset(schema):
        raise ValueError(f"{year}: unsupported schema format")
    questions = schema.loc[schema.qname.eq(TRUST_COLUMN[year]), "question"]
    if len(questions) != 1 or not all(
        word in str(questions.iloc[0]).lower() for word in ["trust", "accuracy"]
    ):
        raise ValueError(
            f"{year}: trust-column semantics do not match the expected question"
        )


def line_chart(summary: pd.DataFrame, destination: Path) -> None:
    """Small, deterministic, script-free SVG. Only aggregate values are rendered."""
    colors = {"adoption_pct": "#1769aa", "positive_trust_pct": "#b64b25"}
    labels = {"adoption_pct": "Uses AI", "positive_trust_pct": "Positive trust"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="820" height="460" viewBox="0 0 820 460" role="img" aria-labelledby="title desc">',
        '<title id="title">AI adoption and positive trust among survey respondents</title>',
        '<desc id="desc">Descriptive percentages with separate adoption and trust denominators. Annual samples differ.</desc>',
        '<rect width="820" height="460" fill="white"/>',
        '<g font-family="sans-serif" fill="#17252f">',
        '<text x="65" y="30" font-size="20">AI adoption and positive trust</text>',
    ]
    x = {2023: 100, 2024: 390, 2025: 680}
    for value in range(0, 101, 20):
        yy = 340 - 2.6 * value
        parts.extend(
            [
                f'<line x1="80" y1="{yy}" x2="720" y2="{yy}" stroke="#d8dee3"/>',
                f'<text x="35" y="{yy+5}" font-size="13">{value}%</text>',
            ]
        )
    for year in x:
        parts.append(f'<text x="{x[year]-18}" y="365" font-size="15">{year}</text>')
    for column, color in colors.items():
        points = " ".join(
            f"{x[int(r.year)]},{340-2.6*getattr(r,column):.3f}"
            for r in summary.itertuples()
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>'
        )
        for r in summary.itertuples():
            v = getattr(r, column)
            xx = x[int(r.year)]
            yy = 340 - 2.6 * v
            label_y = yy - 12 if column == "adoption_pct" else yy + 20
            parts.extend(
                [
                    f'<circle cx="{xx}" cy="{yy:.3f}" r="5" fill="{color}"/>',
                    f'<text x="{xx+9}" y="{label_y:.3f}" fill="{color}" font-size="14">{v:.1f}%</text>',
                ]
            )
    for i, (column, color) in enumerate(colors.items()):
        parts.append(
            f'<text x="{90+i*220}" y="397" fill="{color}" font-size="14">{escape(labels[column])}</text>'
        )
    parts.extend(
        [
            '<text x="65" y="425" font-size="11">Contains information from <a href="https://survey.stackoverflow.co/">Stack Overflow Developer Survey 2023–2025, Stack Exchange, Inc.</a></text>',
            '<text x="65" y="444" font-size="11">Database: <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a> | Chart: kasra-mohebian, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></text>',
            "</g></svg>",
        ]
    )
    destination.write_text("\n".join(parts), encoding="utf-8")


def users_chart(users: pd.DataFrame, destination: Path) -> None:
    frame = users.copy()
    frame["adoption_pct"] = frame["negative_trust_pct"]
    line_chart(frame, destination)
    text = destination.read_text(encoding="utf-8")
    text = text.replace(
        "AI adoption and positive trust among survey respondents",
        "Trust among current AI users",
    )
    text = text.replace(
        "AI adoption and positive trust", "Trust among current AI users"
    )
    text = text.replace(
        "Descriptive percentages with separate adoption and trust denominators. Annual samples differ.",
        "Positive and negative trust among current AI users who answered the trust question. Annual samples differ; these are not the same people over time.",
    )
    text = text.replace("Uses AI", "Negative trust (users)").replace(
        ">Positive trust<", ">Positive trust (users)<"
    )
    destination.write_text(text, encoding="utf-8")


def run(data_root: Path, output: Path) -> None:
    if output.exists():
        raise ValueError(
            "Output already exists; choose a new directory to preserve recorded results"
        )
    (
        rows,
        distributions,
        correlations,
        cross,
        roles,
        organizations,
        experiences,
        inputs,
    ) = ([], [], [], [], [], [], [], [])
    years = [2023, 2024, 2025]
    for year in years:
        path = locate(data_root, year, "survey_results_public.csv")
        schema = locate(data_root, year, "survey_results_schema.csv")
        verify_schema(schema, year)
        wanted = {
            "ResponseId",
            "AISelect",
            "AISent",
            TRUST_COLUMN[year],
            "DevType",
            "OrgSize",
            "YearsCodePro",
        }
        frame = pd.read_csv(path, usecols=lambda col: col in wanted, low_memory=False)
        for optional in ("DevType", "OrgSize", "YearsCodePro"):
            if optional not in frame:
                warnings.warn(
                    f"{year}: {optional} absent; subgroup output omitted", UserWarning
                )
        summary, dist, corr, joint = summarize(frame, year)
        rows.append(summary)
        distributions.extend(dist)
        correlations.append(corr)
        cross.extend(joint)
        d = prepare(frame, year)
        if "DevType" in d:
            # Multi-role responses may appear in several role groups, once in each.
            role_frame = d.assign(role=d.DevType.str.split(";")).explode("role")
            role_frame["role"] = role_frame.role.str.strip()
            role_frame = role_frame.drop_duplicates(["ResponseId", "role"])
            roles.extend(grouped_trust(role_frame, "role", year))
        organizations.extend(grouped_trust(d, "OrgSize", year))
        if "YearsCodePro" in d:
            d["experience"] = d.YearsCodePro.map(experience_group)
            experiences.extend(grouped_trust(d, "experience", year))
        inputs.append(
            {
                "year": year,
                "data_sha256": digest(path),
                "schema_sha256": digest(schema),
                "raw_rows": len(frame),
                "trust_column": TRUST_COLUMN[year],
            }
        )
    summary = pd.DataFrame(rows)
    output.mkdir(parents=True)
    users = users_only_summary(cross)
    tables = {
        "users_only_trust": users,
        "annual_summary": rows,
        "trust_distribution": distributions,
        "trust_sentiment": correlations,
        "adoption_trust_joint": cross,
        "developer_roles": roles,
        "organization_size": organizations,
        "professional_experience": experiences,
    }
    for name, records in tables.items():
        columns = (
            [
                "year",
                "group",
                "adoption_n",
                "adoption_pct",
                "trust_n",
                "positive_trust_pct",
            ]
            if name
            in ["developer_roles", "organization_size", "professional_experience"]
            else None
        )
        pd.DataFrame(records, columns=columns).to_csv(
            output / f"{name}.csv", index=False, float_format="%.10f"
        )
    statistics = {
        "adoption_cramers_v": cramers_v(summary[["using_ai", "not_using_ai"]].values),
        "note": "Descriptive association across annual respondent samples; no causal or population inference.",
    }
    (output / "statistics.json").write_text(json.dumps(statistics, indent=2) + "\n")
    manifest = {
        "sources": inputs,
        "versions": {"numpy": np.__version__, "pandas": pd.__version__},
        "method_version": "1.1",
        "missing_sentiment_policy": "Unsure and missing excluded from paired correlation",
        "group_minimum_adoption_n": 100,
    }
    (output / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    line_chart(summary, output / "adoption-and-trust.svg")
    users_chart(pd.DataFrame(users), output / "users-only-trust.svg")
    print(
        summary[
            [
                "year",
                "adoption_n",
                "adoption_pct",
                "trust_n",
                "positive_trust_pct",
                "negative_trust_pct",
                "neutral_trust_pct",
            ]
        ].to_string(index=False)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        run(args.data_root, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Analysis failed: {error}\n")


if __name__ == "__main__":
    main()
