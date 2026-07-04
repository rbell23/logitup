"""Write newline-delimited JSON logs to a custom file.

Run with:
    uv run python examples/custom_log_file.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from logitup import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    log_file = Path("logs/custom-example.jsonl")
    configure_logging(log_file=log_file)

    logger.info(
        "Configured a custom JSON log file",
        extra={"log_file": str(log_file), "request_id": "req-custom-file"},
    )
    logger.error("Simulated error event", extra={"error_code": "demo-error"})

    print(f"JSON logs written to {log_file}")


if __name__ == "__main__":
    main()
