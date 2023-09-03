import os
import random
import string

from ayo import Template
from rich.console import Console

accepts = string.ascii_letters + string.digits + "-_~[]"

console = Console()

if os.path.exists("ayo.config.json"):
    console.print(
        "[red]ayo.config.json already exists[/red]"
    )
    exit(1)

name = console.input(
    "bin script name? "
    "[d b blue](ayo-script)[/d b blue] "
)

if any(i not in accepts for i in name):
    console.print(
        f"[red]a character is not one of {accepts}[/red]"
    )
    exit(1)

if os.path.exists(name + ".py"):
    console.print(
        "[red]already exists[/red]"
    )
    exit(1)

Template({
    "ayo.config.json": """{
    "bin": "{bin}",
    "with": [],
    "before-scripts": []
}""".replace("{bin}", name),

    name: """#!/usr/bin/python3
print("{rand}")
""".replace("{rand}", random.choice([
    "hot dawg",
    "aint no way",
    "hey user, want some candy?",
    "hi mom",
    "umm... dad...?",
    "how dare you execute this code",
    "python heimer irl found"
]))
}).install("./")
