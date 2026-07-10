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

## GitHub authentication and remote operations

Treat Codex's GitHub connector and the local `gh`/`git` credential store as separate authorization layers.

- Use the GitHub connector first for repository, issue, pull request, review, and metadata workflows when it is available.
- Use local `gh` and `git` for operations the connector does not cover, including current-branch discovery, GitHub Actions logs, fetch/pull/push, commits, and remote checks.
- If a sandboxed `gh auth status` reports an invalid token, do not treat that alone as definitive. Recheck with an approved/elevated `gh auth status -h github.com`, because the macOS keyring token may not be visible inside the sandbox.
- The expected local GitHub account for this project is `rsipakov`; use HTTPS Git remotes with GitHub CLI credential integration unless the user explicitly asks for SSH.
- When reauthentication is needed, prefer `gh auth login -h github.com --web --git-protocol https --skip-ssh-key`, then run `gh auth setup-git -h github.com`. Only create or upload SSH keys when explicitly needed.
- Do not print, persist, commit, or copy GitHub tokens, credentials, or key material.
- Before any remote-changing action such as commit, push, branch creation, PR creation, release creation, or publication, state the target repository, branch, and action unless the user already specified them.

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