#!/usr/bin/python

from ayo import Template, tof

yn = input("Will install example template [Yn] ")
if not tof(yn):
    exit(1)

Template("example-template").install("example-app")