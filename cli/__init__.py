import os
from glob import glob
from pathlib import Path
from typing import Dict, Optional

import click

edge_cli_folder = os.path.dirname(__file__)
cmd_prefix = "cmd_"


class MemehubClickMultiCommand(click.MultiCommand):
    """
    Enables multiple commands in a nested directory structure
    Command filenames must start with cmd_
    """

    @staticmethod
    def filepath_glob(name: Optional[str] = None):
        filename_pattern = cmd_prefix + (name or '*')
        filepath_pattern = edge_cli_folder + f"/**/{filename_pattern}.py"
        filepaths = glob(filepath_pattern, recursive=True)
        if not filepaths:
            raise ValueError(f"Could find files for {filepath_pattern}")
        if name and len(filepaths) != 1:
            raise ValueError("cannot have duplicate names")
        return filepaths

    @staticmethod
    def extract_name(filepath: str):
        """
        filename = cmd_prefix + click.group name
        """
        return Path(filepath).stem.replace(cmd_prefix, "")

    def list_commands(self, ctx: click.Context):
        commands = [self.extract_name(filepath) for filepath in self.filepath_glob()]
        commands.sort()
        return commands

    def get_command(self, ctx: click.Context, name: str):
        filepath = self.filepath_glob(name)[0]
        with open(filepath) as f:
            code = compile(f.read(), filepath, "exec")
            ns: Dict[str, str] = {}
            eval(code, ns, ns)
        return ns[name]


@click.command(cls=MemehubClickMultiCommand)
def entry_point():
    """
    """
    pass
