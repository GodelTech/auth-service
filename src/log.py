import logging.handlers
from pathlib import Path

from src.dyna_config import settings

for path in (
    settings.logging.important_logs_files_path,
    settings.logging.all_logs_files_path,
):
    Path(path).mkdir(parents=True, exist_ok=True)

ALL_LOGS_FILE_PATH = (
    f"{settings.logging.all_logs_files_path}"
    f"{settings.logging.all_logs_filename}"
)
IMPORTANT_LOGS_FILE_PATH = (
    f"{settings.logging.important_logs_files_path}"
    f"{settings.logging.important_logs_filename}"
)

BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {
            "()": "logging.Formatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(message)s",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(client_addr)s "
            "- %(request_line)s - %(status_code)s",
            "use_colors": True,
        },
        "basic_formatter": {
            "()": "logging.Formatter",
            "fmt": BASIC_FORMAT,
        },
    },
    "handlers": {
        "basic_console": {
            "formatter": "basic_formatter",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "console_error": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "console": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file_all": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": ALL_LOGS_FILE_PATH,
            "when": "D",
            "interval": 1,
            "backupCount": 7,
            "level": "DEBUG",
        },
        "file_important": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": IMPORTANT_LOGS_FILE_PATH,
            "when": "D",
            "interval": 1,
            "backupCount": 14,
            "level": "WARNING",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console", "file_all"],
            "level": logging.DEBUG,
            "propagate": False,
        },
        "uvicorn.error": {
            "level": logging.DEBUG,
            "handlers": ["console_error", "file_all", "file_important"],
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["file_all", "console", "file_important"],
            "level": logging.DEBUG,
            "propagate": False,
        },
        "identity_server_provider": {
            "handlers": ["console", "file_all", "file_important"],
            "level": logging.DEBUG,
            "propagate": False,
        },
        "tests": {
            "handlers": ["basic_console"],
            "level": logging.WARNING,
            "propagate": False,
        },
    },
}
