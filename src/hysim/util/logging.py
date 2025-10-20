import logging
import sys
from contextlib import contextmanager
from typing import Any, Generator

import mitsuba as mi
import pkg_resources
import rich.progress as pb
from rich.pretty import pretty_repr


def hysim_version() -> str:
    return pkg_resources.get_distribution("hysim").version

def init_logger(log_level):
    logging.basicConfig(
        format=' %(levelname)-8s %(message)s',
        stream=sys.stdout,
        level=log_level,
        #handlers=[RichHandler(show_time=False,show_path=False, rich_tracebacks=True)]
    )


def pretty(_object) -> str:
    return pretty_repr(_object)

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

    text_format = "[progress.description]{task.description}"
    if frame_count == 1:
        total = None
        transient = True
        columns = (
            pb.TextColumn(text_format),
            pb.BarColumn(),
            pb.TimeElapsedColumn(),
        )
    else:
        total = frame_count
        transient = False
        columns = (
            pb.TextColumn(text_format),
            pb.SpinnerColumn(finished_text=":heavy_check_mark:"),
            pb.BarColumn(),
            CountColumn(),
            pb.TimeElapsedColumn(),
        )

    with pb.Progress(*columns, transient=transient) as pbar:
        task = pbar.add_task(description, total=total)
        yield pbar, task
