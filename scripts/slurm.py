#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = ['click']
# ///
import os
from shutil import which
import subprocess
import shlex
import click
from typing import NoReturn
from contextlib import suppress


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
@click.option("--slurm-sleep", "sleep", default=10.0)
@click.option("--job-name")
@click.pass_context
def slurm(ctx, sleep:float, job_name:str | None):
    sbatch = which("sbatch")
    if sbatch is None:
        error("slurm not installed!")
    if not ctx.args:
        error("no command to run!")
    slurmsh = '.slurm.sh'
    with open(slurmsh, "wt", encoding="utf8") as fp:
        print("#!/bin/bash", file=fp)
        print(f"sleep {sleep}", file=fp)
        print(shlex.join(ctx.args), file=fp)

    if job_name is None:
        for a in ctx.args:
            job_name = a
            break
    try:
        cmds = [sbatch]
        if job_name:
            cmds.append( f"--job-name={job_name}")
        cmds.append(slurmsh)

        run(cmds)
    finally:
        with suppress(OSError, FileNotFoundError):
            os.remove(slurmsh)


if __name__ == "__main__":
    slurm()
