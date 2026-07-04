"""Override specific stdlib logging configuration values.

Run with:
    uv run python examples/override_logger.py
"""

from __future__ import annotations

import logging

from logitup import configure_logging

app_logger = logging.getLogger(__name__)
noisy_logger = logging.getLogger("example.noisy_dependency")


def main() -> None:
    configure_logging(
        level="DEBUG",
        overrides={
            "loggers": {
                "example.noisy_dependency": {"level": "WARNING"},
            },
        },
    )

    app_logger.debug("Application debug logs are enabled")
    noisy_logger.debug("This noisy dependency debug message is suppressed")
    noisy_logger.warning("Dependency warning still appears")


if __name__ == "__main__":
    main()
