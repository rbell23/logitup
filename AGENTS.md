# AGENTS.md

## Project purpose

`logitup` provides small, reusable defaults for Python's stdlib `logging`
package. It should remain a thin configuration/helper package, not a replacement
logging framework.

## Design principles

- Prefer stdlib `logging` and `logging.config.dictConfig`.
- Keep the public API small.
- Do not introduce runtime dependencies without explicit approval.
- Application code should still use:

  ```python
  import logging

  logger = logging.getLogger(__name__)
  ```

- `logitup` should mainly own:
  - default logging config
  - custom formatters
  - custom filters
  - `configure_logging()`

## Development commands

Use `uv`.

```bash
uv run python -m compileall src
```

For a quick smoke test:

```bash
LOGITUP_FILE=/tmp/logitup-test.jsonl uv run python - <<'PY'
import logging
from logitup import configure_logging

configure_logging()
logger = logging.getLogger(__name__)
logger.info("hello", extra={"request_id": "abc123"})
logger.warning("warning")
PY
```

## Compatibility

The package currently targets Python `>=3.12`.

Avoid adding features that require newer Python versions unless the
`requires-python` value is intentionally updated.

## Logging behavior

The default config should continue to log to:

- stdout for `INFO` and below
- stderr for `WARNING` and above
- a newline-delimited JSON file

The JSON log file path should remain configurable by:

- `LOGITUP_FILE`
- `configure_logging(log_file=...)`

## Public API

Be careful when changing exports from `logitup.__init__`.

Current intended public API includes:

- `configure_logging`
- `DEFAULT_LOGGING_CONFIG`
- `DEFAULT_LOG_FILE`
- `LOG_FILE_ENV_VAR`
- `JSONFormatter`
- `MyJSONFormatter`
- `NonErrorFilter`

Avoid breaking these without a clear reason.

## Pull requests

For docs-only changes, no runtime test is required.

For code changes, run at minimum:

```bash
uv run python -m compileall src
```
