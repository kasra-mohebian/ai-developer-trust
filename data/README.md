# Obtain the survey inputs

Download the **2023, 2024 and 2025 Stack Overflow Developer Survey** public results and schemas from the [official survey archive](https://survey.stackoverflow.co/) or [official repository](https://github.com/StackExchange/Survey).

Arrange the original extracted files locally:

```text
data/raw/
  2023/survey_results_public.csv
  2023/survey_results_schema.csv
  2024/survey_results_public.csv
  2024/survey_results_schema.csv
  2025/survey_results_public.csv
  2025/survey_results_schema.csv
```

The alternative original folder names `stack-overflow-developer-survey-2023`, `-2024`, `-2025` are also supported. Do not mix two copies for one year. The pipeline verifies the trust question's meaning against each supplied schema and fails if the expected categories change.

The public repository includes aggregate analysis outputs, not respondent-level records. Source hashes are recorded in `results/provenance.json`; compare hashes before assuming a later corrected download is the same snapshot. The manifest intentionally omits local paths, hostnames and account information.

Source: Stack Overflow Developer Survey, Stack Exchange, Inc. The publisher distributes databases under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) and individual database contents under [DbCL 1.0](https://opendatacommons.org/licenses/dbcl/1-0/). Preserve attribution and applicable notices. See [licensing](../LICENSES.md).
