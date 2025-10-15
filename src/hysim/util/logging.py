import logging
from contextlib import contextmanager
from typing import Any, Generator

import mitsuba as mi
import rich.progress as pb


def set_debug_attr(obj: object, attr_name: str, value: Any):
    """Create an attribute only present in debug mode"""
    if logging.root.getEffectiveLevel() == logging.DEBUG:
        setattr(obj, attr_name, value)

@contextmanager
def log_level(level):
    logger = logging.getLogger()
    old_level = logger.level
    try:
        logger.setLevel(level)
        yield
    finally:
        logger.setLevel(old_level)

@contextmanager
def log_level_mitsuba(level: mi.LogLevel):
    # NOTE: There is no progress bar displayed in the console if mi.variant() is not a scalar variant
    # This is to hide the progress bar if in said variant
    logger = mi.Thread.thread().logger()
    old_level = logger.log_level()
    try:
        logger.set_log_level(level)
        yield logger
    finally:
        logger.set_log_level(old_level)
        del logger

@contextmanager
def progress_bar(frame_count: int, description: str) -> Generator[tuple[pb.Progress, pb.TaskID], Any, None]:
    class CountColumn(pb.ProgressColumn):
        def render(self, _task: "pb.Task") -> pb.Text:
            completed = int(_task.completed)
            _total = int(_task.total) if _task.total is not None else "?"
            unit = " frames"
            total_width = len(str(_total))
            return pb.Text(
                f"{completed:{total_width}d}/{_total}{unit}",
                style="progress.download",
            )

    if frame_count == 1:
        total = None
        transient = True
        columns = (
            pb.TextColumn("[progress.description]{task.description}"),
            pb.BarColumn(),
            pb.TimeElapsedColumn(),
        )
    else:
        total = frame_count
        transient = False
        columns = (
            pb.TextColumn("[progress.description]{task.description}"),
            pb.SpinnerColumn(finished_text=":heavy_check_mark:"),
            pb.BarColumn(),
            CountColumn(),
            pb.TimeElapsedColumn(),
            # FramesRenderedPerSeconds
        )

    with pb.Progress(*columns, transient=transient) as pbar:
        task = pbar.add_task(description, total=total)
        yield pbar, task