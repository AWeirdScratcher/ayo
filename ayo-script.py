#!/usr/bin/python

from ayo import Steps, Template
steps = Steps()

@steps.first
def trick_step() -> str:
    return input("What's your name? ")

@steps.then
def sec_step(name: str) -> int:
    return int(input("How many days since you last take a shower? "))

@steps.then
def third_step(days: int) -> str:
    print(f"Interesting, {days} day(s).")
    return input("I will install something for you! [Yn] ")

@steps.then
def forth_step(yn: str):
    if yn.lower() == "y":
        Template("discord-bot-app").install("app", ignores={
            "main.py": ...
        })

steps.start()