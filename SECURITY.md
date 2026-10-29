# Security and data handling

This repository contains research material and local analysis utilities. It is not a hosted service. Security fixes apply to the current default branch; there is no separate supported-release series.

## Report a security or privacy problem

Use **Security → Report a vulnerability** on this GitHub repository for a private report. Include the affected file or commit and a minimal reproduction using synthetic data. Do not open a public issue containing credentials, personal information or respondent records. Ordinary documentation or research corrections can use public issues without sensitive attachments.

If a credential has been exposed, revoke or rotate it through its provider promptly. Removing a file in a later commit does not remove earlier copies from Git history.

## Safe local use and contributions

- Obtain input datasets from their documented publishers and keep respondent-level files local.
- Inspect changes before running contributed code. Use an isolated Python environment and review dependency changes.
- Keep credentials, local configuration, private reports and participant-level data out of commits, logs and screenshots. Ignore rules reduce accidental additions; they are not a security boundary.
- Use synthetic examples in tests and bug reports. License grants cover the specified original material, not third-party data or papers.

The automated checks have a limited scope. A passing run does not certify that a dataset is anonymous, that dependencies have no vulnerabilities or that every possible security flaw has been excluded.
