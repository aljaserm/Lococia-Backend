# Backend Coding Challenge

Gistapi is a simple HTTP API server implemented in Flask for searching a user's public Github Gists. 

## Endpoints

- `/ping`: A simple ping endpoint to verify the server is up and responding.
- `/api/v1/search`: An endpoint that searches a user's Gists with a regular expression.

## Running the Application

### Using Poetry

1. Install dependencies:
   ```sh
   poetry install
   ```

2. Run the application:
   ```sh
   poetry run flask run --host=0.0.0.0 --port=9876
   ```

### Using Docker

1. Build the Docker image:
   ```sh
   docker build -t gistapi .
   ```

2. Run the Docker container:
   ```sh
   docker run -p 9876:9876 --name gistapi-container gistapi
   ```

## Running Tests

### Using Poetry

```sh
poetry run python -m unittest discover -s tests
```

## Running Code Quality Checkers

### Using Poetry

1. **Run flake8**:
   ```sh
   poetry run flake8 .
   ```

2. **Run black**:
   ```sh
   poetry run black .
   ```

3. **Run isort**:
   ```sh
   poetry run isort .
   ```

## Further Improvements

See the `TODO.md` file for further improvement ideas and architecture considerations.

## Additional Steps

If you want to use Poetry only for dependency management and not for packaging, you can disable package mode by setting `package-mode = false` in your `pyproject.toml` file:

```toml
[tool.poetry]
name = "backend-coding-challenge"
version = "0.1.0"
description = "A simple HTTP API server for searching a user's public Github Gists"
authors = ["Your Name <you@example.com>"]
license = "MIT"
readme = "README.md"
packages = [{include = "gistapi"}]
package-mode = false

[tool.poetry.dependencies]
python = "^3.11"
flask = "^3.0.3"
requests = "^2.27.1"

[tool.poetry.dev-dependencies]
pytest = "^6.2.5"
pytest-flask = "^1.2.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```