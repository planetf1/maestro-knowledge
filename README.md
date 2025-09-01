# maestro-knowledge
A way to configure, ingest, and query knowledge via an AI-native database (e.g., vector database)

## Pre-Commit Hooks

This repository uses `pre-commit` to enforce code style and catch issues before they are committed. The hooks are configured in the `.pre-commit-config.yaml` file.

### Setup

To use the pre-commit hooks, you need to have `pre-commit` installed in your environment.

1.  **Install `pre-commit`:**
    ```bash
    pip install pre-commit
    ```

2.  **Set up the git hooks:**
    ```bash
    pre-commit install
    ```

After this, the pre-commit hooks will run automatically every time you make a commit.

### Configured Checks

The following checks are configured to run on every commit:

-   **`trailing-whitespace`**: Removes any trailing whitespace.
-   **`end-of-file-fixer`**: Ensures that files end with a single newline.
-   **`check-yaml`**: Checks YAML files for syntax errors.
-   **`ruff`**: A fast Python linter that checks for a wide range of issues and can fix many of them automatically.
-   **`ruff-format`**: A fast Python code formatter that ensures a consistent code style.
-   **`detect-secrets`**: Scans for any hardcoded secrets or credentials to prevent them from being committed.
