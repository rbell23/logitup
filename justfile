set dotenv-load := true

lock:
    uv lock

sync:
    uv sync --all-groups

test:
    uv run python -m compileall src
    uv run pytest

fmt:
    uv run ruff format .
    uv run ruff check --fix .
