import shutil
from os import environ, path
from pathlib import Path

import click

# if the HPIDATA environment variable is set (which points to my data)
# use that. Else, just default to ~/data
BASE_PREFIX: Path = Path(environ.get("HPIDATA", path.join(environ["HOME"], "data")))



def get_dir(name: str) -> Path:
    to = (BASE_PREFIX / name).absolute()
    to.mkdir(parents=True, exist_ok=True)
    return to


@click.command()
@click.argument("NAME")
def main(name: str) -> None:
    """
    Helper script to locate a directory to backup to
    """
    click.echo(str(get_dir(name)))


if __name__ == "__main__":
    main(prog_name="backup_to")
