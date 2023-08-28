import json
import os
import re
import requests
import sys
from typing import Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

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
                    "example": "@owner/repo, @owner/repo[branch], dir-name, ..."
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

{contents}
""")
    return 0

def gh_get_ayo_config(owner: str, name: str, branch: str) -> Tuple[str, dict]:
    """Gets the ``ayo.config.json`` from a GitHub repository."""
    base_url = f"https://raw.githubusercontent.com/{owner}/{name}/{branch}"
    
    with console.status(
        f"⚙️  [green]getting config for[/green] "
        f"[blue]{name!r}[/blue] owned by [blue]@{owner}[/blue] "
        f"[d](branch {branch!r})[/d]"
    ):
        
        r = requests.get(
            f"{base_url}/ayo.config.json"
        )
        if r.status_code != 200:
            console.print(
                f"[red]failed to get @{owner}/{name}[/red] - ayo.config.json doesn't exist"
            )
            exit(1)
        
        config = r.json()
        console.print(config, "\n[blue]Got config![/blue]")

    return base_url, config

def gh_download_script_from_config(base_url: str, config: dict) -> str:
    files = [config['bin'], *config.get('with', [])]

    if not os.path.exists(".ayo-scripts"):
        os.mkdir(".ayo-scripts")
        console.print("[d white]created .ayo-scripts[/d white]")

    repo_name = base_url[
        len("https://raw.githubusercontent.com/"):
    ]
    full_path = ".ayo-scripts/" + repo_name.replace("/", "~") + "/"

    if not os.path.exists(full_path):
        os.mkdir(full_path)
        console.print(
            f"[d white]created {full_path}[/d white]"
        )

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "[blue]Fetching required contents...",
            total=config.get("with", 0) + 2 # with + bin (main) + config
        )

        for file in files:
            r = requests.get(base_url + f"/{file}")

            if r.status_code != 200:
                progress.log(f"[red]failed to get {file!r}[/red] (exit status 1)")
                exit(1)

            with open(full_path + file, "wb") as lf:
                lf.write(r.content)

            progress.log(f"collected {file!r}")
            progress.update(task, advance=1)

        progress.log("injecting config...")
    
        with open(full_path + "ayo.config.json", "wb") as file:
            file.write(bytes(
                json.dumps(config, indent=4),
                encoding="utf-8"
            ))

        progress.update(task, advance=1)
    
    console.print(f"\ncollected [green]{repo_name}[/green]")

    return full_path

def get_owner_name_branch(repo: str) -> Tuple[str, str, str]:
    RE_REPO = r"@([-\w0-9]+[-\w0-9]+)\/([-\w0-9]+[-\w0-9]+)"
    RE_BRANCH = r"\[(.+)\]"

    owner, name = re.findall(RE_REPO, repo)[0]
    branch: str = "master"

    if "[" in repo and "]" in repo:
        branch = re.findall(RE_BRANCH, repo)[0]

    return owner, name, branch

def install_and_run(
    args: List[POSSIBLE_TYPES],
    kwargs: Dict[str, POSSIBLE_TYPES]
) -> int:
    if not args:
        show_help("install")
        return 0
    for repo in args:
        owner, name, branch = get_owner_name_branch(repo)
        inferred_path = f".ayo-scripts/{owner}~{name}~{branch}"

        if os.path.exists(inferred_path):
            console.print()
            console.print(
                f"    [green]already exists: {repo}[/green]; using cached\n"
            )
            console.print(
                f"    [d white]pro tip: use [blue]ayo update {repo}[/blue] to update[/d white]\n"
            )
            path = inferred_path + "/"
        
        else:
            base_url, config = gh_get_ayo_config(owner, name, branch)
            path = gh_download_script_from_config(base_url, config)

        if not kwargs.get("install-only", False):
            run_script(path)

def run_script(path: str):
    """Runs the script from its path."""
    with open(path + "ayo.config.json", "r") as file:
        config: dict = json.load(file)
    
    console.print()
    before_scripts = config.get('before-scripts')

    def colored(cmd: str):
        pieces = cmd.split(' ')
        return "[blue]" + pieces[0] + "[/blue] " + " ".join(pieces[1:])

    if before_scripts:
        if isinstance(before_scripts, str):
            console.print("  running scripts")
            console.print(f"  > {colored(before_scripts)}\n")
            os.system(before_scripts)
        else:
            for cmd in before_scripts:
                console.print(f"  > {colored(cmd)}\n")
                os.system(cmd)
    
    cmd = "python " + path + config['bin']
    console.print(f">  {colored(cmd)}")
    console.print()
    result: int = os.system(cmd)

    if result != 0:
        console.print("\n[red]execution failed: [/red] non-zero")
        return 0


def main():
    """The main program."""
    try:
        context: List[str] = sys.argv[1:]

        if not context:
            exit(show_help())

        args, kwargs = get_options(context)

        if not args and "help" in kwargs:
            exit(show_help())

        if args[0].lower() in ['install', 'i']:
            exit(install_and_run(args[1:], kwargs))

    except Exception: # noqa
        console.print_exception()
