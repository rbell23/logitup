"""Basic logitup configuration example.

Run with:
    uv run python examples/basic.py
"""

from __future__ import annotations

import logging

from logitup import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()

    logger.info("Hello from logitup", extra={"request_id": "req-basic"})
    logger.warning("Warnings and above are written to stderr")


if __name__ == "__main__":
    main()
