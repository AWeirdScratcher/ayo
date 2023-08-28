#!/usr/bin/python

import ayo

steps = ayo.Steps()

@steps.first
def first_step():
    proj = input("Name your project: ")
    return proj

@steps.then
def then_do_this(proj):
    print("Installing...")
    ayo.Template("discord-bot-app").install(proj, ignores={
        "venv": ...
    })

steps.start()