import subprocess
from pathlib import Path
import os
import click
from typing import NoReturn
from shutil import which


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
    return get_output([julia, "--startup-file=no", "-e", f"print({expr})"])


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
    real_julia = os.path.join(from_julia(julia, "Sys.BINDIR"), "julia")
    sep = os.path.pathsep
    depot_path = from_julia(real_julia, f'join(DEPOT_PATH, "{sep}")')
    if sep in depot_path:
        td, _ = depot_path.split(sep, maxsplit=1)
    else:
        td = depot_path
    toolsdir = os.path.join(td, toolsdir)
    return real_julia, depot_path, toolsdir


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
