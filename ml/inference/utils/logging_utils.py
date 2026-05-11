from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[%(name)s] "
    "%(message)s"
)


def create_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str | Path] = None,
) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


def log_prediction(
    logger: logging.Logger,
    detector: str,
    label: str,
    confidence: float,
    fake_prob: float,
    risk: str,
) -> None:

    logger.info(
        (
            f"[{detector}] "
            f"label={label} "
            f"confidence={confidence:.4f} "
            f"fake_prob={fake_prob:.4f} "
            f"risk={risk}"
        )
    )


def log_latency(
    logger: logging.Logger,
    component: str,
    latency_ms: float,
) -> None:

    logger.info(
        f"[LATENCY] {component}: {latency_ms:.2f} ms"
    )


def log_exception(
    logger: logging.Logger,
    message: str,
    exc: Exception,
) -> None:

    logger.exception(f"{message}: {str(exc)}")