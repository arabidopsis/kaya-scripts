from __future__ import annotations

import os
import signal
import time
from datetime import datetime

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
    def __init__(self, processing: bool = True):
        self.processing = processing
        self.signal = False

    def __call__(self, signum: int, frame: Any) -> None:
        self.signal = True
        if self.processing:
            return
        raise ContinueException()

    def sleep(self, wait: float) -> None:
        self.processing = False
        time.sleep(wait)
        self.processing = True
@click.command()
@click.option('--sleep', 'wait', default=5.0)
def main(wait:float) -> None:
    def ckpt():
        jobid = os.environ.get('SLURM_JOBID')
        Path(f'checkpoint-{jobid}.txt').touch()
    print('pid=', os.getpid())
    handler = Handler()
    signal.signal(signal.SIGUSR1, handler)
    i= 0
    while True:
        i+=1
        try:
            print('processing', i, datetime.now())
            sum(range(1000000))
            time.sleep(4)
            if handler.signal:
                print("signaled while working")
                raise ContinueException()
            handler.sleep(wait)
        except ContinueException:
            print("awakened by signal....", datetime.now())
            ckpt()
            return


if __name__ == '__main__':
    main()
