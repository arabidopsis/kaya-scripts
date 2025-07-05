#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = ['click']
# ///
import os
from contextlib import suppress
from shutil import which
import shlex
import subprocess
from typing import NoReturn
from uuid import uuid4

import click


def run(cmd: list[str]) -> None:
    p = subprocess.run(
        cmd,
        capture_output=False,
    )
    if p.returncode:
        error("command failed")


def error(msg: str) -> NoReturn:
    m = click.style(msg, fg="red", bold=True)
    raise click.ClickException(m)


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.option("--job-name", help="name for job")
@click.option(
    "--output", help="output filename", type=click.Path(file_okay=True, dir_okay=False)
)
@click.option("--script", help="argument is a script")
@click.pass_context
def slurm(ctx, script: bool, job_name: str | None, output: str | None):
    sbatch = which("sbatch")
    if sbatch is None:
        error("slurm is not installed!")
    if not ctx.args:
        error("no command to run!")

    if ctx.args[0].startswith("-"):
        error(f"unknown option: {ctx.args[0]} (try --help)")

    if script:
        slurmsh = ctx.args[0]
        args = ctx.args[1:]
        if not os.path.isfile(slurmsh):
            error(f"{slurmsh} is not a file!")
        remove = False
    else:
        slurmsh = f".{ctx.args[0]}-{uuid4()}-slurm.sh"
        remove = True
        args = []
        with open(slurmsh, "wt", encoding="utf8") as fp:
            print("#!/bin/bash", file=fp)
            print("sleep 10", file=fp)
            print(shlex.join(ctx.args), file=fp)

    try:
        cmds = [sbatch]
        cmds.append("--time=1:00:00")  # 1 hour max
        if job_name:
            cmds.append(f"--job-name={job_name}")
        if output:
            cmds.append(f"--output={output}")

        cmds.extend([slurmsh, *args])

        run(cmds)
    finally:
        if remove:
            with suppress(OSError, FileNotFoundError):
                os.remove(slurmsh)


if __name__ == "__main__":
    slurm()
