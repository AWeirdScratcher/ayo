def bytes_to_readable(count):
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
