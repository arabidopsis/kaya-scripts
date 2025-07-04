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
    """
    # Use as
    try:
        with GracefulKiller() as prot:
            # do some work uninterrupted
            # ...
            if prot.kill_now:
                print('not now')
            # do some more work
        # do interruptable work
        # we will just be killed here
    except ContinueException:
        print('we got a signal')
        raise SystemExit(0)

    """

    kill_now: bool = False

    def __init__(self, signum: int = signal.SIGTERM) -> None:
        self.kill_now: bool = False
        self.signum = signum
        self._old: Any = None

    def __enter__(self) -> None:
        self._old = signal.signal(self.signum, self.exit_gracefully)

    def __exit__(self, *args: Any) -> None:
        if self._old is not None:
            signal.signal(self.signum, self._old)
            self._old = None
        if self.kill_now:
            raise ContinueException()

    def exit_gracefully(self, *args: Any) -> None:
        self.kill_now = True


class ContinueException(Exception):
    pass


class SigHandler:
    def __init__(self, signum: int, processing: bool = False):
        self.processing = processing
        self.signal = False
        self.signum = signum
        self._old = signal.signal(signum, self)

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

    def teardown(self):
        if self._old is not None:
            signal.signal(self.signum, self._old)

    def __del__(self):
        if self:
            self.teardown()


def get_slurm_jobid() -> str:
    array_job_id = os.getenv("SLURM_ARRAY_JOB_ID")
    if array_job_id is not None:
        array_task_id = os.environ["SLURM_ARRAY_TASK_ID"]
        job_id = f"{array_job_id}_{array_task_id}"
    else:
        job_id = os.environ["SLURM_JOB_ID"]

    assert re.match("[0-9_-]+", job_id)
    return job_id


def requeue() -> int:
    cmd = ["scontrol", "requeue", get_slurm_jobid()]
    try:
        return call(cmd)
    except FileNotFoundError:
        # This can occur if a subprocess call to `scontrol` is run outside a shell context
        # Re-attempt call (now with shell context). If any error is raised, propagate to user.
        # When running a shell command, it should be passed as a single string.
        return call(" ".join(cmd), shell=True)


@click.command()
@click.option("--sleep", "wait", default=5.0)
@click.option("--auto-requeue", is_flag=True)
def test_sigint(wait: float, auto_requeue: bool) -> None:
    """Example of sbatch --signal=SIGUSER@90.

    See `checkpoint.slurm`
    """
    chpt = Path("checkpoint.txt")

    def ckpt(idx):
        print("writing checkpoint", idx)
        with chpt.open("wt") as fp:
            fp.write(f"{idx}")

    def ickpt() -> int:
        if chpt.exists():
            with Path(f"checkpoint.txt").open("rt") as fp:
                return int(fp.read().strip())
        return 0

    print("pid=", os.getpid())
    handler = SigHandler(signal.SIGUSR1)
    start = datetime.now()
    for idx in range(ickpt(), 100000000):
        try:
            n = datetime.now()
            print("processing", idx, n, n - start)
            handler.processing = True
            # do some "work" without interruption
            sum(range(1000000))
            time.sleep(4)
            # done with work
            handler.processing = False
            if handler.signal:
                print("signaled while working")
                raise ContinueException()
            handler.sleep(wait)
        except ContinueException:
            n = datetime.now()
            print("awakened by signal....", n, n - start)
            ckpt(idx)

            if auto_requeue:
                if requeue():
                    print("requeue failed!")
            return


if __name__ == "__main__":
    test_sigint()
