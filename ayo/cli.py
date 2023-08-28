import sys
from typing import Dict, List, Optional, Tuple, Union

from rich.console import Console

console = Console()
POSSIBLE_TYPES = Union[str, bool, int]

def infer_value(plain_text: str) -> POSSIBLE_TYPES:
    """Infers the 'pythonic' value of the plain text.
    
    Args:
        plain_text (str): The plain text.
    """
    if plain_text.startswith('"') and plain_text.endswith('"') \
    or plain_text.startswith("'") and plain_text.endswith("'"):
        return plain_text[1:-1]
    
    elif plain_text.lower() in ["true", "false"]:
        return {"true": True, "false": False}[plain_text]
    
    elif plain_text.isdigit():
        return int(plain_text)
    
    return plain_text # cannot infer; returns str

def get_options(
    values: List[str]
) -> Tuple[List[POSSIBLE_TYPES], Dict[str, POSSIBLE_TYPES]]:
    """Gets options from the argv value.
    
    Args:
        value (list of str): The `sys.argv[1:]` value, recognized as "context."
    """
    args = []
    kwargs = {}

    for item in values:
        if item.startswith(("--", "-")):
            context = item[len("--" if item.startswith("--") else "-"):]
            if "=" not in context:
                kwargs[context] = True
            else:
                objects = context.split('=')
                kwargs[objects[0]] = infer_value(objects[1])
        else:
            args.append(infer_value(item))

    return args, kwargs

def show_help(target_command: Optional[str] = None) -> int:
    """Shows the help message."""

    COMMANDS = [
        {
            "name": "help",
            "help": "Shows this message.",
            "args": [],
            "kwargs": []
        },
        {
            "name": "install",
            "help": "Installs and runs a create-app script.",
            "args": [
                {
                    "name": "scripts",
                    "help": "Scripts to install. Could be a GitHub repo or directory.",
                    "example": "@owner/repo, dir-name, ..."
                }
            ],
            "kwargs": [
                {
                    "name": "install-only",
                    "help": "Install and not run it?",
                    "example": "@owner/repo --install-only"
                }
            ]
        },
        {
            "name": "find",
            "help": "Finds what file runs ayo script.",
            "args": [
                {
                    "name": "script",
                    "help": "The target script to check on. "
                            "Could be a GitHub repo or directory.",
                    "example": "@owner/repo"
                }
            ],
            "kwargs": []
        }
    ]

    contents = ""
    ind = " " * 2
    inner = ind * 2
    deep = " " * 2 + inner

    for command in COMMANDS:
        name = command['name']

        if target_command and name != target_command:
            continue

        info = command['help']
        args = command['args']
        kwargs = command['kwargs']
        contents += f"{ind}ayo [blue]{name}[/blue] - {info}\n\n"

        if args:
            contents += f"{inner}positional args:\n"
            for arg in args:
                argName = arg['name']
                argInfo = arg['help']
                argExample = arg['example']
                contents += f"{deep}[green]{argName}[/green] - {argInfo}\n"

                if argExample:
                    extraSpaces = ' ' * (len(argName + ' - ') - 3)
                    contents += (
                        "[d]"
                        f"{deep}ex.{extraSpaces}ayo [blue]{name}[/blue] {argExample}"
                        "[/d]\n"
                    )

            contents += "\n\n"

        if kwargs:
            contents += f"{inner}keyword-only args:\n"

            for kwarg in kwargs:
                kwargName = kwarg['name']
                kwargInfo = kwarg['help']
                kwargExample = kwarg['example']
                contents += (
                    f"{deep}[yellow]--{kwargName}[/yellow] - "
                    f"{kwargInfo}\n"
                )
                
                if kwargExample:
                    extraSpaces = ' ' * (len('--' + kwargName + ' - ') - 3)
                    contents += (
                        "[d]"
                        f"{deep}ex.{extraSpaces}ayo [blue]{name}[/blue] {kwargExample}"
                        "[/d]\n"
                    )

            contents += "\n\n"

    console.print(f"""
[b]ayo CLI[/b] Wassup?

Available commands:

{contents}
""")
    return 0

def main():
    """The main program."""
    context = sys.argv[1:]

    if not context:
        exit(show_help())

    args, kwargs = get_options(context)

    if not args and "help" in kwargs:
        exit(show_help())
