# /// script
# requires-python = ">=3.10"
# dependencies = ['click']
# ///
import os
import re
import subprocess
from pathlib import Path
from shutil import which, rmtree
from typing import NoReturn
from urllib.parse import urlparse

import click

# e.g. uv run julia-install.py install --main=chloe_main --local https://github.com/ian-small/Chloe.jl.git
# will give you a chloe executable in ~/.local/bin


def get_output(cmd: list[str]) -> str:
    p = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    if p.returncode:
        error(p.stderr.strip())

    return p.stdout.strip()


def from_julia(julia: str, expr: str) -> str:
    return get_output([julia, "-e", f"print({expr})"])


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


def get_project(toolsdir: str = "tools") -> tuple[str, str, str]:
    julia = which("julia")
    if julia is None:
        error("can't find julia executable in PATH!")
    julia = os.path.join(from_julia(julia, "Sys.BINDIR"), "julia")
    sep = os.path.pathsep
    depot_path = from_julia(julia, f'join(DEPOT_PATH, "{sep}")')
    td, _ = depot_path.split(sep, maxsplit=1)
    toolsdir = os.path.join(td, toolsdir)
    return julia, depot_path, toolsdir


def locate_bin_dir(toolsdir: Path, local: bool) -> Path:
    if local:
        bdir: str | Path | None
        bdir = os.environ.get("XDG_BIN_DIR")
        if not bdir:
            bdir = "~/.local/bin"
        bdir = Path(bdir).expanduser()
    else:
        bdir = toolsdir / "bin"

    if not bdir.exists():
        bdir.mkdir()
    return bdir


def getshell(default: str):
    s = os.environ.get("SHELL")
    if s:
        return s.split(os.path.sep)[-1]
    return default


def prefix_option(f):
    return click.option(
        "--prefix",
        metavar="TOOL_DIR",
        show_default=True,
        help="julia tool directory [default is DEPOT_PATH/tools]",
        type=click.Path(dir_okay=True, file_okay=False),
    )(f)


def local_option(f):
    return click.option(
        "-l",
        "--local",
        is_flag=True,
        help="install executable shell script into $XDG_BIN_DIR or ~/.local/bin",
    )(f)


@click.group(
    epilog=click.style('Commands to "install" julia packages\n', fg="magenta"),
)
def cli() -> None:
    pass


@cli.command()
@click.option(
    "-m", "--main", help="main function to invoke (will create a script to run this)"
)
@click.option("--reinstall", is_flag=True, help="reinstall (overwrite) this tool")
@local_option
@prefix_option
@click.option(
    "-p", "--package", help="package name. Taken from first repo name if not set."
)
@click.argument("github_repos", nargs=-1, required=True)
def install(
    prefix: str | Path | None,
    package: str | None,
    github_repos: tuple[str, ...],
    main: str | None,
    reinstall: bool,
    local: bool,
) -> None:
    """install Chloe, Emma etc into their own project and create a script to run them."""

    if package is None:
        repo = github_repos[0]
        if repo.startswith("https://"):
            u = urlparse(repo)
            package = u.path.split("/")[-1]
            package = package.split(".")[0]
        else:
            package = repo

    # get actual julia exe location
    toolsdir: str | Path

    julia, depot_path, toolsdir = get_project()

    if prefix is not None:
        toolsdir = prefix

    toolsdir = Path(toolsdir).expanduser()
    project = toolsdir / f"{package}_project.jl"
    if project.exists():
        if not reinstall:
            error(f"{project} already exists!")
        rmtree(project)

    def pkg(repo: str) -> str:
        if repo.startswith("https://"):
            return f'Pkg.add(url="{repo}")'
        return f'Pkg.add("{repo}")'

    def add(*repos: str) -> None:
        pkgs = "; ".join(pkg(r) for r in repos)
        run([julia, f"--project={project}", "-e", f"using Pkg; {pkgs}"])

    if not toolsdir.exists():
        toolsdir.mkdir(parents=True)

    click.secho(f"creating project: {project}", fg="yellow")
    run([julia, "-e", f'using Pkg; Pkg.generate("{project}")'])

    click.secho(f"adding packages to {project}", fg="yellow")
    add(*github_repos)

    if not main:
        return

    SHELL = f"""#!/bin/bash
export JULIA_DEPOT_PATH="{depot_path}"
exec {julia} --project="{project}" \\
    --startup-file=no -e 'using {package}; {main}()' -- "$@"
"""

    bdir = locate_bin_dir(toolsdir, local)

    script = bdir / package.lower()
    click.secho(f"writing: {script}", fg="green", bold=True)
    with open(script, "wt", encoding="utf8") as fp:
        fp.write(SHELL)

    script.chmod(0o755)


@cli.command()
@local_option
@prefix_option
@click.argument("package", required=True)
@click.argument(
    "julia_scripts",
    type=click.Path(file_okay=True, exists=True, dir_okay=False),
    nargs=-1,
    required=True,
)
def executify(
    package: str,
    julia_scripts: tuple[str | Path, ...],
    local: bool,
    prefix: str | Path | None,
) -> None:
    """create a runnable script for julia "script" files"""

    toolsdir: str | Path
    julia, depot_path, toolsdir = get_project()
    if prefix is not None:
        toolsdir = prefix
    toolsdir = Path(toolsdir).expanduser()
    project = toolsdir / f"{package}_project.jl"
    if not project.exists():
        pf = "" if not prefix else f" --prefix={prefix}"
        error(
            f'can\'t find package "{package}". Run: install --package={package}{pf} [REPOS]...'
        )

    bdir = locate_bin_dir(toolsdir, local)

    for julia_script in julia_scripts:
        julia_script = Path(julia_script).expanduser().resolve()

        SHELL = f"""#!/bin/bash
export JULIA_DEPOT_PATH="{depot_path}"
exec {julia} --project="{project}" \\
    --startup-file=no "{julia_script}" "$@"
"""

        script = bdir / julia_script.name
        e = script.exists()
        w = "overwriting" if e else "writing"
        fg = "yellow" if e else "green"
        click.secho(f"{w}: {script}", fg=fg, bold=True)
        with open(script, "wt", encoding="utf8") as fp:
            fp.write(SHELL)

        script.chmod(0o755)


## extract SHELL environment setup for micromamba env
## so instead of micromamba activate myenv
## we can just do `source /path/to/myenv.sh` and be done with it
## Means we don't need to give anyone access to micromamba and
## *also* have it "installed"


@cli.command()
@click.option("-d", "--deactivate", help="generate deactivation script", is_flag=True)
@click.option(
    "-a", "--absolute", help="generate an absolute PATH", is_flag=True
)
@click.option("-o", "--output", help="output filename",
              type=click.Path(file_okay=True, dir_okay=False))
@click.option("-s", "--shell", help="shell to use. e.g. bash, tcsh etc.")
@click.argument("environment", required=False)
def mamba(
    deactivate: bool,
    absolute: bool,
    output: str | None,
    shell: str | None,
    environment: str | None,
) -> None:
    """generate mamba activation/deactivate scripts"""
    micromamba = which("micromamba")
    if micromamba is None:
        error("no micromamba to run!")

    PS1 = re.compile(b"(:?\n|^)(PS1=.*)")
    PATH=re.compile(b"export PATH='([^']+)'")
    if environment is None:
        environment = os.environ.get('CONDA_DEFAULT_ENV')
        if environment is None:
            error("can't determine environment")

    name = os.path.basename(environment)

    shell = shell or getshell("posix")

    inenv = "CONDA_DEFAULT_ENV" in os.environ

    if deactivate:
        if not inenv:
            error("you are not within a conda environment!")

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
        if not absolute:
            env = {"PATH": "${PATH}"}
        else:
            env = None


    p = subprocess.run(cmd, text=False, capture_output=True, env=env)
    if p.returncode:
        error(p.stderr.decode("utf-8").strip())

    out = p.stdout
    # remove PS1
    out = PS1.sub(b"", out)
    if env is not None:
        out = PATH.sub(rb'export PATH="\1"', out)  # single to double quotes
    # elif deactivate:
    #     # just remove path
    #     out = PATH.sub(b'', out)
    elif deactivate and os.environ.get('UV'): # running under uv
        m = PATH.search(out)
        if m:
            s = os.path.pathsep.encode('ascii')
            paths = m.group(1).split(s)
            # remove uv path
            p = s.join(paths[1:])
            out = PATH.sub(b"export PATH='" + p + b"'", out)
                

    fname = f"{name}{ext}" if not output else output
    click.secho(f"writing: {fname}", fg="green")
    with open(fname, "wb") as fp:
        fp.write(out)

if __name__ == "__main__":
    cli()
