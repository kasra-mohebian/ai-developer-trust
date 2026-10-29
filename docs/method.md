# Method and interpretation

## Questions

1. How does reported current AI-tool use differ across the 2023–2025 survey samples?
2. How does positive, neutral and negative trust in output accuracy differ?
3. Among the same respondents, how are trust and sentiment associated, and how do trust responses differ between users and non-users?
4. What descriptive differences appear by role, professional experience and organization size?

## Data and eligibility

Each input is an independent annual response file. IDs are checked for uniqueness within a year and never used to link people across years. The main sample includes respondents with a nonmissing AISelect answer. It is not restricted to professional developers. Trust and correlation analyses have additional nonmissing-answer requirements. Denominators accompany every percentage.

Current use includes the daily, weekly and monthly/infrequent `Yes` categories in 2025. Planning to use AI is not current use. The wording/options evolved between years; this limits comparability.

## Schema alignment

| Concept | 2023 | 2024 | 2025 |
|---|---|---|---|
| Current use | AISelect | AISelect | AISelect |
| Trust in output accuracy | AIBen | AIAcc | AIAcc |
| Sentiment | AISent | AISent | AISent |

The 2023 field named AIAcc contains hoped-for benefits, not trust. The mapping is based on the actual question in the supplied schema; reusing names across years without checking their meaning changes the construct.

## Calculations

Positive trust is exactly `Highly trust` or `Somewhat trust`; negative is exactly `Highly distrust` or `Somewhat distrust`; neutral is `Neither trust nor distrust`. Unknown trust/adoption categories cause an error. No substring classification is used.

For paired Spearman correlation, trust and sentiment are selected from the same respondent row. Trust and sentiment use ordered 1–5 mappings. `Unsure` sentiment remains unmapped and is excluded from this paired statistic; it is counted separately. Spearman's rho is computed as Pearson correlation of average ranks. No p-values or causal interpretation are reported.

The headline adoption-minus-positive-trust difference uses different eligible answer groups. It is a difference in descriptive percentages, not the percentage of people using AI while distrusting it. `adoption_trust_joint.csv` instead cross-tabulates both answers from the same respondent, with within-use-group denominators.

Wilson intervals describe binomial sample uncertainty for adoption. They do not account for nonresponse, recruitment, self-selection or survey design. Cramer's V for the annual adoption table uses `min(rows - 1, columns - 1)`; it is an association measure, not an adjustment for sampling bias.

For subgroup summaries, groups require at least 100 adoption respondents. Multi-role respondents contribute once to each selected role, so role groups overlap and should not be summed as disjoint populations. Organization size is used as reported. Professional experience uses explicit year bands and excludes unparseable/missing values.

## Limits

These are self-selected cross-sectional samples, not a representative census or longitudinal panel. Missingness and eligibility differ by question and year. Association does not identify why trust changed, whether AI causes distrust, or whether developers are compelled to adopt tools. The analysis measures survey answers, not actual coding speed, code quality or security outcomes. The synthetic test cases check implementation behavior; they do not validate survey measurement or external generalizability.

## Implementation

`core.py` contains schema/category semantics and statistics. `__main__.py` loads selected columns, validates schemas, produces seven aggregate tables and records source hashes. It also emits a deterministic static SVG without external plotting libraries. An existing output directory is rejected to protect saved results.

## Review correction: eligible population and missing columns

Version 1.1 adds `users_only_trust.csv` and `users-only-trust.svg`. The denominator is current AI users with a mapped, nonmissing trust answer. The preserved 2024 source has zero non-user trust answers; do not treat its pooled trust estimate as a like-for-like comparison with all respondents in the other years. This observed pattern alone is not a complete reconstruction of survey routing.

`YearsCodePro` is absent from the 2025 input, so no 2025 professional-experience output is available. Optional missing subgroup columns now emit warnings. Developer-role and organization-size categories also change across years (including 2025's `Less than 20 employees`); category names are retained, not silently harmonized. Compare subgroups within a year unless an explicit mapping is justified.

Experience bands in revised code are `0-1 years`, `2 years`, `3-5 years`, `6-10 years`, `11-20 years`, `21+ years`. Historical `professional_experience.csv` retains its original labels; its `1-2 years` bucket contains only 2 and its `20+ years` bucket contains values above 20. Counts have not been reassigned. The first bucket includes `Less than 1 year` and exactly 1.
