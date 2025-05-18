import logging
from pathlib import Path

import colorama
import structlog

from game.settings import get_settings

cr = structlog.dev.ConsoleRenderer(
    columns=[
        # Render the timestamp without the key name in yellow.
        structlog.dev.Column(
            "timestamp",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Fore.YELLOW,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=str,
            ),
        ),
        # Render the event without the key name in bright magenta.
        structlog.dev.Column(
            "event",
            structlog.dev.KeyValueColumnFormatter(
                key_style=None,
                value_style=colorama.Style.BRIGHT + colorama.Fore.MAGENTA,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=str,
            ),
        ),
        # Default formatter for all keys not explicitly mentioned. The key is
        # cyan, the value is green.
        structlog.dev.Column(
            "",
            structlog.dev.KeyValueColumnFormatter(
                key_style=colorama.Fore.CYAN,
                value_style=colorama.Fore.GREEN,
                reset_style=colorama.Style.RESET_ALL,
                value_repr=str,
            ),
        ),
    ]
)

settings = get_settings()

log_path = settings.LOG_FILE
log_level = logging.getLevelName(settings.LOG_LEVEL.upper())


structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=(
        structlog.WriteLoggerFactory(file=Path(log_path).open("wt"))
        if log_path
        else None
    ),
)

if log_path is None:
    structlog.configure(processors=structlog.get_config()["processors"][:-1] + [cr])


def get_logger(name: str):
    logger = structlog.get_logger(name)
    return logger
