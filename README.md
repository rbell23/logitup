# logitup

Small, reusable defaults for Python's stdlib `logging` package.

## Defaults

`configure_logging()` configures stdlib logging to write:

- human-readable console logs split across stdout/stderr
  - `INFO` and below: stdout
  - `WARNING` and above: stderr
- newline-delimited JSON logs to a file
  - default: `logs/app.jsonl`
  - override with the `LOGITUP_FILE` environment variable
  - or pass `log_file=...` directly

## Usage

```python
import logging

from logitup import configure_logging

configure_logging()

logger = logging.getLogger(__name__)
logger.info("Hello from logitup", extra={"request_id": "abc123"})
```

Use a custom JSON log file path:

```python
configure_logging(log_file="logs/my-service.jsonl")
```

Use JSON logs on the console too:

```python
configure_logging(formatter="json")
```

Override stdlib `dictConfig` values when needed:

```python
configure_logging(
    level="DEBUG",
    overrides={
        "loggers": {
            "botocore": {"level": "WARNING"},
        },
    },
)
```

For full control, pass an entire stdlib `dictConfig` mapping:

```python
configure_logging(config=my_logging_config)
```
