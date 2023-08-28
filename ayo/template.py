from enum import Enum
from typing import Any, Optional

class then(Enum):
    never = 1

class Template:
    """Represents an ayo script template.
    
    Args:
        contents (dict of str: str | :obj:`then`): The contents.
    """
    __slots__ = (
        'contents',
    )
    contents: list[dict]

    def __init__(
        self,
        contents: str | dict[str, str | then]
    ):
        self.contents = []

        for item in contents:
            pass

    @staticmethod
    def convert_dict_to_list(
        data: dict[str, str | dict[str, Any]], 
        prefix: str = "", 
        result: Optional[list] = None
    ):
        if result is None:
            result = []

        for key, value in data.items():
            if isinstance(value, str):
                result.append(prefix + key)
            elif isinstance(value, dict):
                result.append(f"make dir: {prefix}{key}")
                Template.convert_dict_to_list(value, prefix + key + "/", result)

        return result
