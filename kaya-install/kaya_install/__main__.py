from . import mamba
from . import julia

__all__ = ["mamba", "julia"]

from .cli import cli

if __name__ == "__main__":
    cli()
