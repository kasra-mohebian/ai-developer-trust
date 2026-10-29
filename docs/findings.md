# Findings from the reproduced analysis

The [annual table](../results/annual_summary.csv) contains counts and denominators, not only rounded headline percentages.

| Year | Adoption answers | Current users | Trust answers | Positive | Negative | Neutral |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 87,973 | 39,042 | 61,396 | 25,879 | 16,680 | 18,837 |
| 2024 | 60,907 | 37,662 | 37,302 | 16,055 | 11,327 | 9,920 |
| 2025 | 33,720 | 26,469 | 33,260 | 10,904 | 15,201 | 7,155 |

The headline comparison now uses current AI users answering trust: positive trust is 48.2%, 43.0% and 39.3% in 2023, 2024 and 2025. The table above retains the pooled historical counts; its populations differ across years. Question eligibility, survey wording, missingness and the mix of respondents differ across years.

## Use and distrust can coexist

The headline difference between usage and trust percentages does not itself identify individuals with both characteristics. [The joint table](../results/adoption_trust_joint.csv) uses the same respondent's answers to show positive, neutral and negative trust within current-use groups. This is the appropriate table to inspect for coexistence, subject to the missing-trust filter.

## Trust and sentiment

[Paired rank correlations](../results/trust_sentiment.csv) exclude missing and `Unsure` sentiment responses. These associations describe answers to two related attitude questions. They do not measure actual tool reliability or establish a direction of causation. Samples and exact coefficients are in the table.

## Subgroups

[Developer roles](../results/developer_roles.csv), [experience](../results/professional_experience.csv) and [organization size](../results/organization_size.csv) provide descriptive comparisons. Role groups overlap. Small adoption groups are omitted; trust denominators can still be smaller. These comparisons are not controlled estimates of experience or organization effects.

## What is not concluded

The tables do not establish why trust changes, whether using AI reduces trust, how much productivity changes, or which tools are more secure. No percentage for a proposed cause of trust erosion is inferred from unrelated questions. The analysis does not claim to be the first study of this topic.

The 2025 source lacks professional-experience data (`YearsCodePro`); no 2025 experience comparison is supported. Role and organization categories also change across years. See the explicit review correction in [method](method.md).
