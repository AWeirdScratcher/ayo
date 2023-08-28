# ayo

Run Python "create app" scripts from the web and GitHub repositories.

## Installation

```ps
$ pip install --upgrade ayo
```

## Install & Run A Script

To install and run script(s), you can use the `ayo i` command (which means `install`).

You can either run scripts from GitHub or run them locally from a specific directory.

```ps
$ ayo i @username/repo @username/repo[branch] dir-name
```

## Creating Your Script

To create your script, try:

```ps
$ ayo new
```

Two files will be generated: `ayo.config.json` and `ayo-script.py`. Currently, `ayo` itself provides two built-in utilities:

- Template: Used to create an app from a template folder or do it manually
- Steps: Represents steps for your application, and caches previous data even when canceled.

First, let's take a look at `ayo.config.json`. This configuration JSON file determines which file(s) `ayo` needs to run. Below is the default content that was generated using the `new` command:

```json
{
    "bin": "ayo-script.py",
    "with": [],
    "before-scripts": []
}
```

- `bin`: The file that runs the script. Think of it as `main.py`
- `with`: The files to also contain when downloading this from GitHub. Usually used when the `bin` file requires modules. This field should only contain `.py` files. Optional.
- `before-scripts`: Scripts to run before running the `bin` file. Optional.

Then, take a look at `ayo-script.py`. You should see the default script:

```python
#!/usr/bin/python

from ayo import Template, true_or_false

yn = input("Can I install something for you?")
if not true_or_false(yn):
    exit(1)

Template({
    "main.py": "# surprise! new app!"
}).install()
```

Decent code! But let's twist it a little bit: let's edit it so we can try out the `Steps` and `Template` feature!

It goes something like this:

```python
#!/usr/bin/python

from ayo import Steps

steps = Steps()

@steps.first # first step
def hello_world():
    print("Hello, World!")

@steps.then # then...
def ask_for_install(data):
    # 'data': data returned from the previous function
    # in this case, None!
    return input("Can I install something for you?")

@steps.then
def write_or_exit(data: str):
    # the 'data' is given from the 'input()'
    if data.lower() != "yes":
        exit(1)

    Template({
        "main.py": "# surprise! new app!",
        "another-dir": {
            "README.md": "More content!"
        }
    }).install("new-app")

steps.start() # start!
```

With `Steps`, whenever the user sneakly (or maybe they just want to go out for a bit) pressed `^C` which causes `KeyboardInterrupt`, the program writes a new file (`_ayo$cache.py`) for cache-storing so that the next time they can quickly pick up from where they left off and continue their journey!

Let's try out our freshly made script by running:

```ps
$ ayo run
```

## Available Commands

To check the available commands, run:

```ps
$ ayo --help
```

