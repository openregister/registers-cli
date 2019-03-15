from typing import List
from .core import Action, Command # NOQA
from .parser import parse, load # NOQA


def read(filepath: str) -> List[Command]:
    """
    # Example

    ```
    from registers import rsf

    commands = rsf.read('country.rsf')
    ```
    """

    with open(filepath, 'r') as handle:
        return parse(handle)


def dump(commands: List[Command]) -> str:
    return "\n".join([str(command) for command in commands]) + "\n"
