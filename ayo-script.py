from ayo import Template, Steps, tof

steps = Steps(cache=False)

@steps.first
def ask() -> str:
    return input(
        "Will install an example template under 'example-app/'. [Yn] "
    )

@steps.then
def install(data: str) -> None:
    if not tof(data):
        return

    Template("example-template").install("example-app")

steps.start()