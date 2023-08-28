#!/usr/bin/python

from ayo import Template, true_or_false

yn = input("Can I install something for you?")
if not true_or_false(yn):
    exit(1)

Template({
    "main.py": "# surprise! new app!"
}).install()
