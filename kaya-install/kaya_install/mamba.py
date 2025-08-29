import os
import re
import subprocess
from shutil import which


import click
from .cli import cli
from .utils import error, get_project, getshell


## extract SHELL environment setup for micromamba env
## so instead of micromamba activate myenv
## we can just do `source /path/to/myenv.sh` and be done with it
## Means we don't need to give anyone access to micromamba and
## *also* have it "installed"


@cli.command()
@click.option("-d", "--deactivate", help="generate deactivation script", is_flag=True)
@click.option("-a", "--absolute", help="generate an absolute PATH", is_flag=True)
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
    absolute: bool,
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
            error("no micromamba to run!")
        else:
            micromamba = exe

    _, _, toolsdir = get_project()

    toolsbin = os.path.join(toolsdir, "bin")

    PS1 = re.compile(b"(:?\n|^)(PS1=.*)")
    PATH = re.compile(b"export PATH='([^']+)'")
    if environment is None:
        environment = os.environ.get("CONDA_DEFAULT_ENV")
        if environment is None:
            error("can't determine environment")

    name = os.path.basename(environment)

    shell = shell or getshell("posix")

    inenv = "CONDA_DEFAULT_ENV" in os.environ

    if deactivate:
        if not inenv:
            error("you are not within a conda environment! activate one!")

        cmd = [micromamba, "shell", "deactivate", "--shell", shell]
        ext = "-deactivate.sh"
        env = None
    else:
        if inenv:
            error("you are in a conda environment! deactivate it!")

        cmd = [
            micromamba,
            "shell",
            "activate",
            environment,
            "--shell",
            shell,
        ]
        ext = "-activate.sh"

        env = {"MAMBA_ROOT_PREFIX": os.environ["MAMBA_ROOT_PREFIX"]}
        if not absolute:
            env.update({"PATH": f"{toolsbin}:${{PATH}}"})

    p = subprocess.run(cmd, text=False, capture_output=True, env=env)
    if p.returncode:
        error(p.stderr.decode("utf-8").strip())

    out = p.stdout
    # remove PS1
    out = PS1.sub(b"", out)
    if no_path:
        out = PATH.sub(b"", out)
    else:
        if env is not None:
            out = PATH.sub(rb'export PATH="\1"', out)  # single to double quotes
        elif deactivate and os.environ.get("UV"):  # running under uv
            m = PATH.search(out)
            if m:
                s = os.path.pathsep.encode("ascii")
                paths = m.group(1).split(s)
                # remove uv path
                p = s.join(paths[1:])
                out = PATH.sub(b"export PATH='" + p + b"'", out)

    fname = f"{name}{ext}" if not output else output
    click.secho(f"writing: {fname}", fg="green")
    with open(fname, "wb") as fp:
        fp.write(out)
