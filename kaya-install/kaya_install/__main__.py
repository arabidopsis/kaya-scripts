from . import mamba
from . import julia
from .cli import cli

__all__ = ["mamba", "julia"]

if __name__ == "__main__":
    cli()
