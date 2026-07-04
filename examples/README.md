# Examples

Small runnable examples for `logitup`.

Run any example from the repository root with `uv`:

```bash
uv run python examples/basic.py
uv run python examples/custom_log_file.py
uv run python examples/json_console.py
uv run python examples/override_logger.py
```

## Included examples

- `basic.py` configures the default stdout/stderr console logs and JSON file logs.
- `custom_log_file.py` writes JSON logs to a custom newline-delimited JSON file.
- `json_console.py` uses the JSON formatter for console output too.
- `override_logger.py` shows how to override specific `dictConfig` values.
