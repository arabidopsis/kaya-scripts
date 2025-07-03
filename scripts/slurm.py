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
from uuid import uuid4


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
    context_settings=dict(ignore_unknown_options=True, 
                          allow_extra_args=True)
)
@click.option("--slurm-sleep", "sleep", default=10.0)
@click.option("--job-name", help='give a name to this job')
@click.option("--script", help='argument is a script')
@click.pass_context
def slurm(ctx, sleep:float, job_name:str | None, script:bool):
    sbatch = which("sbatch")
    if sbatch is None:
        error("slurm is not installed!")
    if not ctx.args:
        error("no command to run!")
    if script:
        slurmsh = ctx.args[0]
        if not os.path.isfile(slurmsh):
            error(f"{slurmsh} is not a file!")
    
        remove = False
    else:
        slurmsh = f'.slurm-{uuid4()}.sh'
        remove = True
        with open(slurmsh, "wt", encoding="utf8") as fp:
            print("#!/bin/bash", file=fp)
            print(f"sleep {sleep}", file=fp)
            print(shlex.join(ctx.args), file=fp)

    if job_name is None:
        for a in ctx.args:
            if not a.startswith('-'):
                job_name = a
                break
    try:
        cmds = [sbatch]
        if job_name:
            cmds.append( f"--job-name={job_name}")
        cmds.append(slurmsh)

        run(cmds)
    finally:
        if remove:
            with suppress(OSError, FileNotFoundError):
                os.remove(slurmsh)


if __name__ == "__main__":
    slurm()
