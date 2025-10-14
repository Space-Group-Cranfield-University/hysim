import logging
from contextlib import contextmanager
from typing import Any

import mitsuba as mi


class CustomMitsubaFormatter(mi.Formatter):
    def __init__(self, frame_index: int):
        super().__init__()
        self.frame_index = frame_index

    def format(self, level: mi.LogLevel, cname, fname, line, msg):
        return f" {level.name.upper():8} {chr(0x02523)}{chr(0x02501)} Frame {self.frame_index} - {msg}"

    @staticmethod
    @contextmanager
    def log(frame_index: int):
        """Creates a custom mitsuba formatter to match HySim and sets mitsuba's logger to use
        it. Also sets the log level to mi.LogLevel.Info to make sure the start and finished
        rendering messages are displayed."""

        # NOTE: There is no progress bar displayed in the console if mi.variant() is not a scalar variant
        mitsuba_logger = mi.Thread.thread().logger()
        log_level = mitsuba_logger.log_level()
        try:
            mitsuba_logger.set_formatter(CustomMitsubaFormatter(frame_index))
            mitsuba_logger.set_log_level(mi.LogLevel.Info)
            yield mitsuba_logger
        finally:
            mitsuba_logger.set_log_level(log_level)
            del mitsuba_logger

def setdebugattr(obj: object, attr_name: str, value: Any):
    """Create an attribute only present in debug mode"""
    if logging.root.getEffectiveLevel() == logging.DEBUG:
        setattr(obj, attr_name, value)

@contextmanager
def log_level_context(level):
    logger = logging.getLogger()
    old_level = logger.level
    try:
        logger.setLevel(level)
        yield
    finally:
        logger.setLevel(old_level)

@contextmanager
def log_level_context_mitsuba(level: mi.LogLevel):
    # NOTE: There is no progress bar displayed in the console if mi.variant() is not a scalar variant
    # This is to hide the progress bar
    logger = mi.Thread.thread().logger()
    log_level = logger.log_level()
    try:
        logger.set_log_level(level)
        yield logger
    finally:
        logger.set_log_level(log_level)
        del logger