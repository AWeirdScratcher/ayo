import os
from typing import Any, Callable, List, Optional, Union

from rich.console import Console

TYPES = Optional[Union[str, int, float, bool]]
console = Console()

class Steps:
    """Represents steps."""
    __slots__ = (
        "current",
        "steps",
        "data",
        "remember"
    )
    current: int
    steps: List[Callable]
    data: List[Any]
    remember: bool

    def __init__(self, *, remember: bool = True):
        self.current = 0
        self.steps = []
        self.data = []
        self.remember = remember

        if remember and os.path.exists("_ayo$cache.py"):
            cache_module = __import__("_ayo$cache")
            completions = getattr(cache_module, "_completions", [])
            self.data = [
                i for i in completions if i
            ] # noqa

            if self.data:
                console.print(
                    f"✨ [blue]Restored to Q{len(self.data)}[/blue]",
                    f"(you entered {self.data[-1]!r})",
                    overflow="ellipsis"
                )
                
    def first(self, function: Callable[..., TYPES]) -> None:
        """Registers the very first task. Acts as a decorator.
        
        Args:
            function ((...) -> str | int | float | bool): The function.

        Example:
            .. code-block :: python

                steps = Steps()
                @steps.first
                def first_step():
                    print("I print!")
        """
        self.steps.append(function)

    def then(self, function: Callable[[TYPES], TYPES]) -> None:
        """Register tasks after the first one. Acts as a decorator.

        Once this function is called, the data returned from the previous step will be passed as an arg.
        
        Args:
            function ((data: str | int | float | bool | None) -> str | int | float | bool | None): The function.
        """
        self.steps.append(function)

    def start(self):
        """Starts the process."""
        data = self.data
        steps = self.steps
        collected_data = [None if i >= len(data) else data[i] for i in range(len(steps))]
        begin = len(data)

        try:
            for index, f in enumerate(steps):
                if index < begin:
                    continue

                if index == 0:
                    _next_data = f()
                else:
                    _next_data = f(collected_data[index - 1])

                collected_data[index] = _next_data

        except KeyboardInterrupt:
            if self.remember:
                with open("_ayo$cache.py", "w", encoding="utf-8") as file:
                    file.write("_completions=[" + ", ".join([
                        f"{i!r}" for i in collected_data
                    ]) + "]")

            exit(1)

        # safe exit
        if os.path.exists("_ayo$cache.py"):
            os.remove("_ayo$cache.py")
