"""Use JSON formatting for console logs too.

Run with:
    uv run python examples/json_console.py
"""

from __future__ import annotations

import logging

from logitup import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging(formatter="json", level="DEBUG")

    logger.debug("Debug event", extra={"feature": "json-console"})
    logger.info("Info event", extra={"request_id": "req-json-console"})
    logger.warning("Warning event", extra={"remaining_retries": 2})


if __name__ == "__main__":
    main()
