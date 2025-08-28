# maestro-knowledge
A way to configure, ingest, and query knowledge via an AI-native database (e.g., vector database)

## Pre-commit Hooks

This repository uses `pre-commit` to enforce code style and catch issues before they are committed. To use the pre-commit hooks, you need to have `pre-commit` installed.

### Setup

1.  Install `pre-commit`:
    ```bash
    pip install pre-commit
    ```

2.  Set up the git hooks:
    ```bash
    pre-commit install
    ```
    Now, `pre-commit` will run automatically on `git commit`!

### Configured Checks

The following checks are configured to run:

*   **`trailing-whitespace`**: Trims trailing whitespace from files.
*   **`end-of-file-fixer`**: Ensures that files end with a single newline.
*   **`check-yaml`**: Checks YAML files for syntax errors.
*   **`check-added-large-files`**: Prevents large files from being committed to the repository.
*   **`ruff`**: A fast Python linter and code formatter. It checks for a wide range of issues and can automatically fix many of them.
*   **`gitleaks`**: Scans the repository for hardcoded secrets and credentials.
