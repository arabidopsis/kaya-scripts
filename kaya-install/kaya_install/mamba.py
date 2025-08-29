import os
from pathlib import Path
import re
import subprocess
from shutil import which


import click
from .cli import cli
from .utils import error, getshell


## extract SHELL environment setup for micromamba env
## so instead of micromamba activate myenv
## we can just do `source /path/to/myenv.sh` and be done with it
## Means we don't need to give anyone access to micromamba and
## *also* have it "installed"


@cli.command()
@click.option("-d", "--deactivate", help="generate deactivation script", is_flag=True)
@click.option("--no-path", help="don't output PATH", is_flag=True)
@click.option(
    "-o",
    "--output",
    help="output filename",
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.option("-s", "--shell", help="shell to use. e.g. bash, tcsh etc.")
@click.argument("environment", required=False)
def mamba(
    deactivate: bool,
    output: str | None,
    shell: str | None,
    environment: str | None,
    no_path: bool,
) -> None:
    """generate mamba activation/deactivate scripts"""
    micromamba = which("micromamba")
    if micromamba is None:
        exe = os.environ.get("MAMBA_EXE")
        if exe is None:
            error("No micromamba executable to run!")
        else:
            micromamba = exe

    PS1 = re.compile(b"(:?\n|^)(PS1=.*)")
    PATH = re.compile(b"export PATH='([^']+)'")
    if environment is None:
        environment = os.environ.get("CONDA_DEFAULT_ENV")
        if environment is None:
            if deactivate:
                error("Please activate an environment")
            error("Can't determine environment for activation")

    name = os.path.basename(environment)

    shell = shell or getshell("posix")

    inenv = "CONDA_DEFAULT_ENV" in os.environ

    if deactivate:
        if not inenv:
            error("You are not within a conda environment. Please activate one!")

        cmd = [micromamba, "shell", "deactivate", "--shell", shell]
        ext = "-deactivate.sh"
    else:
        if inenv:
            error("You are in a conda environment! Please deactivate it!")

        cmd = [
            micromamba,
            "shell",
            "activate",
            environment,
            "--shell",
            shell,
        ]
        ext = "-activate.sh"

        # env = {"MAMBA_ROOT_PREFIX": os.environ["MAMBA_ROOT_PREFIX"]}
        # if not absolute:
        #     env.update({"PATH": f"{toolsbin}:${{PATH}}"})

    p = subprocess.run(cmd, text=False, capture_output=True)
    if p.returncode:
        error(p.stderr.decode("utf-8").strip())

    out = p.stdout
    # remove PS1
    out = PS1.sub(b"", out)
    if no_path:
        out = PATH.sub(b"", out)
    else:
        if deactivate and os.environ.get("UV"):  # running under uv
            m = PATH.search(out)
            if m:
                s = os.path.pathsep.encode("ascii")
                paths = m.group(1).split(s)
                # remove uv path
                p = s.join(paths[1:])
                out = PATH.sub(b"export PATH='" + p + b"'", out)

    fname = Path(f"{name}{ext}" if not output else output)
    click.secho(f"writing: {fname}", fg="green")
    fname.write_bytes(out)
