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