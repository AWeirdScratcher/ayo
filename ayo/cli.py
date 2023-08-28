import json
import os
import re
import requests
import shutil
import sys
from contextlib import suppress
from typing import Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from .template import Template
from .utils import tof


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
            "name": "run",
            "help": "Run scripts.",
            "args": [
                {
                    "name": "scripts",
                    "help": "(optional) The scripts to run. Could be a GitHub repo or directory. "
                            "If not given, runs scripts in the current directory.",
                    "example": "."
                }
            ],
            "kwargs": []
        },
        {
            "name": "update",
            "help": "Updates multiple scripts at once.",
            "args": [
                {
                    "name": "scripts",
                    "help": "The scripts to update. Could only be GitHub repos.",
                    "example": "@owner/repo, @owner/repo[branch], ..."
                }
            ],
            "kwargs": []
        },
        {
            "name": "uninstall",
            "help": "Uninstall multiple scripts at once.",
            "args": [
                {
                    "name": "scripts",
                    "help": "The scripts to uninstall. Could only be GitHub repos.",
                    "example": "@owner/repo, @owner/repo[branch], ..."
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

{f"Help for '{target_command}'" if target_command else "Available Commands:"}

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
    """GitHub: Download a script from a config dictionary.
    
    Args:
        base_url (str): The base URL. Should start with ``https://raw.githubusercontent.com/``.
        config (dict): The config dictionary.
    """
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
    
    console.print(f"\ncollected and created [green]{full_path}[/green]")

    return full_path

def get_owner_name_branch(repo: str) -> Tuple[str, str, str]:
    """Gets the owner, repository name and branch from the repo name the user provided.
    
    Args:
        repo (str): The repo name input by the user.
    """
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
    """Installs the script and runs it."""
    if not args:
        show_help("install")
        return 0

    for repo in args:
        if repo.startswith("@"):
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
        else:
            if kwargs.get("install-only", False):
                console.print(
                    "[d white]info: using `--install-only` for local files doesn't make sense.[/d white]"
                )

            if not os.path.exists(repo):
                console.print(f"[red]directory does not exist: {repo}[/red]")
                return 1
            
            return run_script(repo + ("" if repo.endswith(("/", "\\")) else "/"))

def run_script(path: str):
    """Runs the script from its path.
    
    Make sure it ends with a slash.

    Args:
        path (str): The path.
    """
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

def update_scripts(
    args: List[POSSIBLE_TYPES],
    kwargs: Dict[str, POSSIBLE_TYPES]
) -> int:
    """Updates scripts."""
    if not args:
        show_help("update")
        return 0

    for repo in args:
        owner, name, branch = get_owner_name_branch(repo)
        inferred_path = f".ayo-scripts/{owner}~{name}~{branch}"

        if os.path.exists(inferred_path):
            console.print(
                f"[red]removing {inferred_path} (and everything under it)[/red]"
            )
            shutil.rmtree(inferred_path)

            console.print(f"updating [blue]{repo}[/blue]")
            base_url, config = gh_get_ayo_config(owner, name, branch)
            gh_download_script_from_config(base_url, config)

            console.print(f"updated {repo} successfully")

        else:
            console.print(
                f"{repo!r} was not installed."
            )
            yn = console.input("[blue]?[/blue] Would you like to install it? [Yn] ")

            if tof(yn):
                base_url, config = gh_get_ayo_config(owner, name, branch)
                gh_download_script_from_config(base_url, config)

            return 0

def uninstall_scripts(
    args: List[POSSIBLE_TYPES],
    kwargs: Dict[str, POSSIBLE_TYPES]
) -> int:
    if not args:
        show_help("uninstall")
        return 0

    for repo in args:
        owner, name, branch = get_owner_name_branch(repo)
        inferred_path = f".ayo-scripts/{owner}~{name}~{branch}"

        if os.path.exists(inferred_path):
            yn = console.input("[red]are you sure?[/red] I have a family! [Yn] ")

            if not tof(yn):
                exit(1)

            with console.status(f"[red]uninstalling {repo!r}...[/red]"):
                shutil.rmtree(inferred_path)
    
            console.print(f"[green]uninstalled {repo!r}[/green]")
        else:
            console.print(f"cannot uninstall {repo!r}: does not exist")
            exit(1)

    console.print("finished.")
    return 0

def raw_run(
    args: List[POSSIBLE_TYPES],
    kwargs: Dict[str, POSSIBLE_TYPES]
) -> int:
    if not args:
        if not os.path.exists("ayo.config.json"):
            console.print(f"[red]error: ayo.config.json does not exist[/red]")
            return 1

        return run_script("./")

    for repo in args:
        if repo.startswith("@"):
            owner, name, branch = get_owner_name_branch(repo)
            inferred_path = f".ayo-scripts/{owner}~{name}~{branch}"

            if not os.path.exists(inferred_path):
                console.print(f"[red]directory does not exist: {inferred_path}[/red]")
                return 1
            
            run_script(inferred_path + "/")
            continue

        if not os.path.exists(repo):
            console.print(f"[red]directory does not exist: {repo}[/red]")
            return 1
        
        return run_script(repo + ("" if repo.endswith(("/", "\\")) else "/"))

def init_new_project(
    args: List[POSSIBLE_TYPES],
    kwargs: Dict[str, POSSIBLE_TYPES]
) -> int:
    """Creates a new project for the user."""
    if os.path.exists("ayo.config.json"):
        console.print("[red]file already exists: ayo.config.json[/red]")
        return 1
    
    fn = args[0] if args else "ayo-script.py"

    if os.path.exists(fn):
        console.print(f"[red]file already exists: {fn}[/red]")
        return 1
    
    Template({
        f"{fn}.py": """\
#!/usr/bin/python

from ayo import Template, true_or_false

yn = input("Can I install something for you?")
if not true_or_false(yn):
    exit(1)

Template({
    "main.py": "# surprise! new app!"
}).install("new-app")
""",

        "ayo.config.json": """\
{
    "bin": "{fn}.py",
    "with": [],
    "before-scripts": []
}
""".replace('{fn}', fn)
    }).install(".")

    return 0


def main():
    """The main program."""
    try:
        context: List[str] = sys.argv[1:]

        if not context:
            exit(show_help())

        args, kwargs = get_options(context)

        if (not args and "help" in kwargs) \
        or (args and args[0] == "help"):
            exit(show_help())

        if args[0].lower() in ['install', 'i']:
            exit(install_and_run(args[1:], kwargs))

        elif args[0].lower() == 'update':
            exit(update_scripts(args[1:], kwargs))

        elif args[0].lower() == 'uninstall':
            exit(uninstall_scripts(args[1:], kwargs))

        elif args[0].lower() == 'run':
            exit(raw_run(args[1:], kwargs))

        elif args[0].lower() == 'clean-cache':
            with suppress(FileNotFoundError):
                os.remove("_ayo$cache.py")

            exit(0)

        elif args[0].lower() in ['init', 'new']:
            exit(init_new_project(args[1:], kwargs))

        else:
            exit(install_and_run(args, kwargs))

    except Exception: # noqa
        console.print_exception()
