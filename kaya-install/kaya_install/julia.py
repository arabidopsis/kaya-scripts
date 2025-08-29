from pathlib import Path
from shutil import rmtree
from urllib.parse import urlparse

import click

from .cli import cli
from .utils import get_project, error, run, locate_bin_dir

# e.g. kaya install --local --main=chloe_main  https://github.com/ian-small/Chloe.jl.git
# will give you a chloe executable in ~/.local/bin


def prefix_option(f):
    return click.option(
        "--tools",
        metavar="TOOL_DIR",
        show_default=True,
        help="julia tool directory [default is $JULIA_DEPOT_PATH/tools]",
        type=click.Path(dir_okay=True, file_okay=False),
    )(f)


def local_option(f):
    return click.option(
        "-l",
        "--local",
        is_flag=True,
        help="install executable shell script into $XDG_BIN_DIR or ~/.local/bin",
    )(f)


@cli.group(
    help=click.style('Commands to "install" julia packages\n', fg="magenta"),
)
def julia() -> None:
    """Manage julia packages and executables"""


@julia.command()
@click.option(
    "-m", "--main", help="main function to invoke (will create a script to run this)"
)
@click.option("--reinstall", is_flag=True, help="reinstall (overwrite) this tool")
@local_option
@prefix_option
@click.option(
    "-p", "--package", help="package name. Taken from first repo name if not set."
)
@click.argument("github_repos_or_julia_packages)", nargs=-1, required=True)
def install(
    tools: str | Path | None,
    package: str | None,
    github_repos_or_julia_packages: tuple[str, ...],
    main: str | None,
    reinstall: bool,
    local: bool,
) -> None:
    """install Chloe, Emma etc into their own project and create a script to run them."""

    if package is None:
        repo = github_repos_or_julia_packages[0]
        if repo.startswith("https://"):
            u = urlparse(repo)
            package = u.path.split("/")[-1]
            package = package.split(".")[0]
        else:
            package = repo

    # get actual julia exe location
    toolsdir: str | Path

    julia, depot_path, toolsdir = get_project()

    if tools is not None:
        toolsdir = tools

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
        run([julia,  "--startup-file=no",  f"--project={project}", "-e", f"using Pkg; {pkgs}"])

    if not toolsdir.exists():
        toolsdir.mkdir(parents=True)

    click.secho(f"creating project: {project}", fg="yellow")
    run([julia, "--startup-file=no", "-e", f'using Pkg; Pkg.generate("{project}")'])

    click.secho(f"adding packages to {project}", fg="yellow")
    add(*github_repos_or_julia_packages)

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
    script.write_text(SHELL, encoding="utf8")

    script.chmod(0o755)


@julia.command()
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
    """create a runnable script for julia "script" files based on package PACKAGE.

    See install --package=PACKAGE github repos or...packages
    """

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
        script.write_text(SHELL, encoding='utf8')

        script.chmod(0o755)
