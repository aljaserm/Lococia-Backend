# Code Quality Tools

This project uses the following tools to ensure code quality:

- **Flake8**: for linting Python code.
- **Black**: for formatting Python code.
- **isort**: for sorting imports.
- **pre-commit**: for running code quality tools before every commit.

## How to Use

### Flake8

To run Flake8:

```sh
poetry run flake8
```

### Black

To format the code with Black:

```sh
poetry run black .
```

### isort

To sort imports with isort:

```sh
poetry run isort .
```

### Pre-commit Hooks

Pre-commit hooks are automatically run before each commit. To manually run the pre-commit hooks on all files:

```sh
poetry run pre-commit run --all-files
```

## Configuration

The configuration for these tools is located in the `pyproject.toml` and `.pre-commit-config.yaml` files.
```