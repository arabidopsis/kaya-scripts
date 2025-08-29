import click


@click.group(
    epilog=click.style(
        'Commands to "install" julia packages setup conda environments etc.\n',
        fg="magenta",
    ),
)
def cli() -> None:
    pass
