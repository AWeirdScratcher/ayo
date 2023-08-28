import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

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
    contents: List[str]

    def __init__(
        self,
        contents: Union[str, Dict[str, Union[str, Dict]]]
    ):
        if isinstance(contents, str):
            self.contents = []

            if not os.path.exists(".ayo-templates"):
                raise NotADirectoryError("Directory not found: .ayo-templates")
            
            if not os.path.isdir(".ayo-templates"):
                raise NotADirectoryError("'.ayo-templates' must be a directory.")
            
            target_directory = f".ayo-templates/{contents}"
            if not os.path.exists(target_directory) \
            or not os.path.isdir(target_directory):
                raise NotADirectoryError(
                    f"{target_directory!r} is not a directory or does not exist."
                )
            
            for root, dirs, files in os.walk(target_directory):
                for _dir in dirs:
                    self.contents.append(f"?mk:{os.path.join(root, _dir)}")

                for file in files:
                    self.contents.append(os.path.join(root, file))

        elif isinstance(contents, dict):
            self.contents = Template.convert_dict_to_list(contents)

    @staticmethod
    def convert_dict_to_list(
        data: Dict[str, Union[str, Dict[str, Any]]],
        prefix: str = "", 
        result: Optional[list] = None
    ) -> List[str]:
        """Converts a directory dictionary to valid contents data."""
        if result is None:
            result = []

        for key, value in data.items():
            if isinstance(value, str):
                result.append(prefix + key)
            elif isinstance(value, dict):
                result.append(f"?mk:{prefix}{key}")
                Template.convert_dict_to_list(value, prefix + key + "/", result)

        return result
