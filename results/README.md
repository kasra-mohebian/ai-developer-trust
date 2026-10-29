# Aggregate results and data-source notice

Contains information from the **Stack Overflow Developer Survey, Stack Exchange, Inc., 2023–2025**, available from the [official survey archive](https://survey.stackoverflow.co/). The source databases are made available under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/); individual database contents use the [Database Contents License 1.0](https://opendatacommons.org/licenses/dbcl/1-0/).

The aggregate CSV collection is made available under ODbL 1.0 for applicable database rights. It is published without respondent-level source records. The [Python pipeline](../src/trust_analysis/__main__.py), [core transformations](../src/trust_analysis/core.py), [input instructions](../data/README.md) and [provenance manifest](provenance.json) describe how the aggregates were produced from the annual snapshots. These provide the method of alterations for the documented analysis; they do not grant new rights over the publisher's inputs.

The original generated SVG is a produced chart under CC BY 4.0, with the underlying survey database attribution and ODbL notice retained. JSON files document computation/provenance. See [LICENSES.md](../LICENSES.md) for the file scopes. Keep this source notice associated with redistributed results and retain the applicable database terms.

## Method versions

This directory retains historical outputs alongside later derived tables. `provenance.json` records method 1.0; the current pipeline reports method 1.1. The current run preserves the aggregate counts, but `professional_experience.csv` has revised boundary labels (`2 years`, `21+ years`), the provenance method version changes, and the original SVG can differ by a trailing newline. The users-only table and chart were added during review. Existing numerical outputs are not silently replaced. See [method notes](../docs/method.md).
