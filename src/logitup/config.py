"""Default stdlib logging configuration for logitup."""

from __future__ import annotations

import atexit
import copy
import logging
import logging.config
import os
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Any, Literal

LogLevel = int | str
FormatterName = Literal["simple", "json"]

LOG_FILE_ENV_VAR = "LOGITUP_FILE"
DEFAULT_LOG_FILE = "logs/app.jsonl"

DEFAULT_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
        "json": {
            "()": "logitup.formatters.JSONFormatter",
            "fmt_keys": {
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "function": "funcName",
                "line": "lineno",
                "thread_name": "threadName",
            },
        },
    },
    "filters": {
        "non_error": {
            "()": "logitup.formatters.NonErrorFilter",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "filters": ["non_error"],
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "json_file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": DEFAULT_LOG_FILE,
            "encoding": "utf-8",
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["stdout", "stderr", "json_file"],
            "respect_handler_level": True,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["queue_handler"],
    },
}


def configure_logging(
    *,
    level: LogLevel = "INFO",
    formatter: FormatterName = "simple",
    log_file: str | os.PathLike[str] | None = None,
    config: Mapping[str, Any] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> None:
    """Configure stdlib logging with logitup defaults.

    Args:
        level: Root logger level, stdout handler level, and JSON file level.
        formatter: Built-in formatter to use for console handlers.
        log_file: JSON log file path. Defaults to the ``LOGITUP_FILE``
            environment variable, then ``logs/app.jsonl``.
        config: Full ``logging.config.dictConfig`` mapping. When supplied, this
            replaces ``DEFAULT_LOGGING_CONFIG`` as the base config.
        overrides: Recursive updates applied to the selected base config before
            calling ``logging.config.dictConfig``.
    """

    logging_config = copy.deepcopy(config or DEFAULT_LOGGING_CONFIG)

    logging_config.setdefault("root", {})["level"] = level
    handlers = logging_config.setdefault("handlers", {})
    if "stdout" in handlers:
        handlers["stdout"]["level"] = level
        handlers["stdout"]["formatter"] = formatter
    if "stderr" in handlers:
        handlers["stderr"]["formatter"] = formatter
    if "json_file" in handlers:
        resolved_log_file = Path(
            log_file or os.environ.get(LOG_FILE_ENV_VAR, DEFAULT_LOG_FILE)
        )
        resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers["json_file"]["level"] = level
        handlers["json_file"]["filename"] = str(resolved_log_file)

    if overrides is not None:
        _deep_update(logging_config, overrides)

    logging.config.dictConfig(logging_config)
    _start_queue_listeners()


def _start_queue_listeners() -> None:
    """Start QueueHandler listeners created by dictConfig, if present."""

    seen: set[int] = set()
    for logger in [logging.getLogger(), *logging.Logger.manager.loggerDict.values()]:
        if not isinstance(logger, logging.Logger):
            continue
        for handler in logger.handlers:
            listener = getattr(handler, "listener", None)
            if listener is None or id(listener) in seen:
                continue
            seen.add(id(listener))
            if getattr(listener, "_thread", None) is None:
                listener.start()
                atexit.register(listener.stop)


def _deep_update(
    target: MutableMapping[str, Any], updates: Mapping[str, Any]
) -> MutableMapping[str, Any]:
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(target.get(key), MutableMapping):
            _deep_update(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
    return target
