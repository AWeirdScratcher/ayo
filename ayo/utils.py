import random

def bytes_to_readable(count) -> str:
    """Converts bytes to a human readable string.
    
    Args:
        count (int): The byte count.
        """
    if count < 1024:
        return f"{count} byte{'s' if count == 0 or count > 1 else ''}"
    elif count < 1024 ** 2:
        return f"{count / 1024:.2f} KB"
    elif count < 1024 ** 3:
        return f"{count / (1024 ** 2):.2f} MB"
    elif count < 1024 ** 4:
        return f"{count / (1024 ** 3):.2f} GB"
    else:
        return f"{count / (1024 ** 4):.2f} TB"


def true_or_false(_input: str, *, false_if_unknown: bool = True) -> bool:
    """Checks whether the input provided by the user (Yn) is true or not.

    Args:
        _input (str): The input.
        false_if_unknown (bool, optional): Whether to return ``False`` if received unrecognized input.
    """
    if _input.lower() in ("y", "yes", "yup", "yep", "true"):
        return True

    elif _input.lower() in ("n", "no", "nope", "nah", "nawh", "false"):
        return False
    
    elif false_if_unknown:
        return False

    else:
        raise ValueError(f"Unrecognized Yn choice: {_input!r}")

tof = true_or_false # alias

def random_fact() -> str:
    """Generates a random fact (FOR AYO ONLY)."""
    return random.choice([
        "You can think of this as a fake pip",

        "The disk of the Milky Way galaxy is about 100,000 light years in diameter"
        " (one light year is about 9.5 x 1015 meters).",

        "Calgary's elevation is approximately 1,048 m (3,438 ft) above sea level downtown, "
        "and 1,084 m (3,557 ft) at the airport.",

        "Dumbledore is an expert at Transfiguration too, having taught the subject before becoming headmaster.",

        "I made ayo because I was bored, and found out woah, nobody has used this name before!",

        "'ZIP' is actually an acronym for Zone Improvement Plan.",

        "I've always wondered who asked since 2021!",

        "Most Belgian waffle recipes are yeast-based, to get that crispy texture.",

        "Bacon is actually red meat.",

        "Earth is by far the most dynamic planet when seen from space.",

        "When a cat rubs you, he is marking you with his scent, claiming you as \"his.\"",

        "You cannot hear any sounds in near-empty regions of space."
    ])