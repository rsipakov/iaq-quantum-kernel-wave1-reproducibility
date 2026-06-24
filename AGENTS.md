# AGENTS.md

## Repository purpose

This repository contains the public reproducibility artifacts accompanying the
manuscript on quantum-kernel diagnostics for duplicate-sensor monitoring.

Everything in this repository must be suitable for public release.

## Required context

Before making changes, read:

- `README.md`;
- relevant environment and dependency files;
- relevant scripts, notebooks, manifests, and provenance documentation;
- any task-specific instructions present in this repository.

## Scientific integrity

Do not invent or silently infer:

- data;
- numerical values;
- experimental parameters;
- results;
- citations;
- execution history;
- artifact provenance.

Do not manually alter numerical artifacts merely to make them agree with the
manuscript.

If an artifact, script, table, figure, or documented value is inconsistent,
report the discrepancy instead of silently choosing or editing one version.

## Public-release requirements

Do not add:

- private or restricted data;
- credentials, tokens, secrets, or account identifiers;
- internal working notes or review comments;
- machine-specific absolute paths;
- artifacts with unverified provenance;
- references to unavailable private files as though they were public.

Use repository-relative paths in documentation, scripts, notebooks, and
configuration files.

## Reproducibility

Before modifying or generating an artifact:

1. identify its documented source;
2. identify the generating script or procedure;
3. identify the required inputs and configuration;
4. confirm that existing files will not be unintentionally overwritten;
5. preserve units, labels, seeds, parameters, and output schemas.

Prefer reproducible generation from documented scripts over manual editing.

Do not install, upgrade, or download dependencies or external data unless the
task explicitly requires it.

## File changes

Creating new files is allowed when they have a clear reproducibility or
documentation purpose.

Use descriptive filenames and existing directories. Do not create vague
versions such as `final_new`, `updated`, or `latest`.

Do not delete, rename, or overwrite important artifacts unless explicitly
requested.

## Git and publication actions

Do not commit, push, create releases, publish packages, upload artifacts, or
open pull requests unless explicitly requested.

Before finishing, inspect the diff for:

- accidental numerical changes;
- private information;
- absolute local paths;
- unrelated modifications;
- missing provenance;
- inconsistencies with repository documentation.

## Completion report

At the end of the task, report:

- files read;
- files created;
- files modified;
- commands and checks performed;
- provenance verified;
- assumptions made;
- unresolved reproducibility or publication risks.