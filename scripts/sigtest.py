from __future__ import annotations
import re
import os
import signal
import time
from datetime import datetime
from subprocess import call

from pathlib import Path

from typing import Any

import click


# from https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    kill_now: bool = False

    def __init__(self) -> None:
        self.kill_now: bool = False
        self.old: Any = None

    def __enter__(self) -> None:
        self.old = signal.signal(signal.SIGTERM, self.exit_gracefully)

    def __exit__(self, *args: Any) -> None:
        if self.old is not None:
            signal.signal(signal.SIGTERM, self.old)
            self.old = None
        if self.kill_now:
            raise ContinueException()

    def exit_gracefully(self, *args: Any) -> None:
        self.kill_now = True


class ContinueException(Exception):
    pass


class Handler:
    def __init__(self, signum: int, processing: bool = True):
        self.processing = processing
        self.signal = False
        signal.signal(signum, self)

    def __call__(self, signum: int, frame: Any) -> None:
        self.signal = True
        if self.processing:
            return
        raise ContinueException()

    def sleep(self, wait: float) -> None:
        self.processing = False
        time.sleep(wait)
        self.processing = True

    def check(self):
        if self.processing:
            return
        if self.signal:
            raise ContinueException()

def get_slurm_jobid() -> str:
    array_job_id = os.getenv("SLURM_ARRAY_JOB_ID")
    if array_job_id is not None:
        array_task_id = os.environ["SLURM_ARRAY_TASK_ID"]
        job_id = f"{array_job_id}_{array_task_id}"
    else:
        job_id = os.environ["SLURM_JOB_ID"]

    assert re.match("[0-9_-]+", job_id)
    return job_id

def requeue():
    cmd = ["scontrol", "requeue", get_slurm_jobid()]
    call(cmd)

@click.command()
@click.option("--sleep", "wait", default=5.0)
@click.option('--auto-requeue', is_flag=True)
def main(wait: float, auto_requeue:bool) -> None:
    chpt = Path(f"checkpoint.txt")
    def ckpt(idx):
        with chpt.open('wt') as fp:
            fp.write(f'{idx}')
    def ickpt() ->int:
        if chpt.exists():
            with Path(f"checkpoint.txt").open('rt') as fp:
                return int(fp.read().strip())
        return 0
    print("pid=", os.getpid())
    handler = Handler(signal.SIGUSR1)
    start = datetime.now()
    for idx in range(ickpt(), 100000000):
        try:
            n = datetime.now()
            print("processing", idx, n, n - start)
            sum(range(1000000))
            time.sleep(4)
            if handler.signal:
                print("signaled while working")
                raise ContinueException()
            handler.sleep(wait)
        except ContinueException:
            n = datetime.now()
            print("awakened by signal....", n, n - start)
            ckpt()

            if auto_requeue:
                requeue()
            return


if __name__ == "__main__":
    main()
