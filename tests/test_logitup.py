from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from logitup import LOG_FILE_ENV_VAR, configure_logging


@pytest.fixture(autouse=True)
def reset_logging() -> Iterator[None]:
    yield
    _stop_queue_listeners()
    logging.shutdown()
    root = logging.getLogger()
    root.handlers.clear()
    root.filters.clear()


def test_default_logs_to_console_and_json_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    configure_logging()

    logger = logging.getLogger("tests.default")
    logger.info("hello", extra={"request_id": "abc123"})
    logger.warning("careful")
    _stop_queue_listeners()

    captured = capsys.readouterr()
    assert "INFO | hello" in captured.out
    assert "WARNING | careful" not in captured.out
    assert "WARNING | careful" in captured.err
    assert "INFO | hello" not in captured.err

    log_file = tmp_path / "logs" / "app.jsonl"
    records = _read_json_lines(log_file)

    assert [record["message"] for record in records] == ["hello", "careful"]
    assert records[0]["level"] == "INFO"
    assert records[0]["logger"] == "tests.default"
    assert records[0]["request_id"] == "abc123"
    assert records[1]["level"] == "WARNING"


def test_log_file_env_var_is_respected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log_file = tmp_path / "env.jsonl"
    monkeypatch.setenv(LOG_FILE_ENV_VAR, str(log_file))
    configure_logging()

    logging.getLogger("tests.env").info("from env")
    _stop_queue_listeners()

    records = _read_json_lines(log_file)
    assert records[0]["message"] == "from env"


def test_log_file_argument_overrides_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_log_file = tmp_path / "env.jsonl"
    explicit_log_file = tmp_path / "explicit.jsonl"
    monkeypatch.setenv(LOG_FILE_ENV_VAR, str(env_log_file))
    configure_logging(log_file=explicit_log_file)

    logging.getLogger("tests.argument").info("from argument")
    _stop_queue_listeners()

    assert not env_log_file.exists()
    records = _read_json_lines(explicit_log_file)
    assert records[0]["message"] == "from argument"


def test_overrides_patch_dict_config(tmp_path: Path) -> None:
    log_file = tmp_path / "override.jsonl"
    configure_logging(
        log_file=log_file,
        overrides={
            "loggers": {
                "tests.overrides": {
                    "level": "ERROR",
                    "propagate": True,
                }
            }
        },
    )

    logger = logging.getLogger("tests.overrides")
    logger.warning("hidden")
    logger.error("visible")
    _stop_queue_listeners()

    records = _read_json_lines(log_file)
    assert [record["message"] for record in records] == ["visible"]


def _read_json_lines(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def _stop_queue_listeners() -> None:
    seen: set[int] = set()
    for logger in [logging.getLogger(), *logging.Logger.manager.loggerDict.values()]:
        if not isinstance(logger, logging.Logger):
            continue
        for handler in logger.handlers:
            listener = getattr(handler, "listener", None)
            if listener is None or id(listener) in seen:
                continue
            seen.add(id(listener))
            if getattr(listener, "_thread", None) is not None:
                listener.stop()
