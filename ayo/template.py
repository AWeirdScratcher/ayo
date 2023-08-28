import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from .utils import bytes_to_readable


class then(Enum):
    never = 1

class Template:
    r"""Represents an ayo script template.
    
    Args:
        contents (dict of str: str | dict of str: str | ...): The contents.

    Example:
        .. code-block :: python

            from ayo import Template
            template = Template("my-ayo-template-dir")
            # or do it manually (with custom files & contents)
            template = Template({
                "main.py": "with open('data/data.json') as file:\n  file.read()",
                "README.md": "# Welcome!\nThis is my project generator.",
                "data": {
                    "data.json": '{\n  "happy": true\n}'
                }
            })
    """
    __slots__ = (
        'contents',
    )
    contents: List[Dict[str, str]]

    def __init__(
        self,
        contents: Union[str, Dict[str, Any]]
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
                relroot = root[len(target_directory + "/"):]
                for _dir in dirs:
                    self.contents.append({
                        "fn": f"?mk:{os.path.join(relroot, _dir)}"
                    })

                for fileName in files:
                    _path = os.path.join(root, fileName)
                    with open(_path, "rb") as file:
                        self.contents.append({
                            "fn": os.path.join(relroot, fileName),
                            "content": file.read()
                        })

        elif isinstance(contents, dict):
            self.contents = Template.convert_dict_to_list(contents)

    def install(
        self, 
        project_name: str, 
        *, 
        ignores: Dict[str, Any] = {}
    ):
        """Installs contents for the user from this template.
        
        Args:
            project_name (str): The project name defined by the user.
            ignores (dict of str: str | dict of str: :obj:`Any`, optional): A directory dict representing which files 
                and directories to exclude.
        """
        if os.path.exists(project_name):
            raise FileExistsError(f"Directory or file already exists: {project_name!r}")

        ignores = Template.convert_dict_to_list(ignores)
        root: str = project_name if project_name.endswith(("/", "\\")) else (project_name + "/")
        os.mkdir(root)

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[green]Creating new project...", total=len(self.contents))

            for content in self.contents:
                if any(
                    content['fn'].startswith(item['fn']) \
                    or content['fn'].startswith(item['fn'][len("?mk:"):]) \
                    for item in ignores
                ):
                    progress.update(task, advance=1)
                    ignored = (root + content['fn']).replace("\\", "/")
                    progress.log(
                        f"[d white](ignored cmd {ignored})[/d white]"
                    )
                    continue

                if content['fn'].startswith("?mk:"):
                    directory: str = content['fn'][len('?mk:'):]
                    os.mkdir(root + directory)
                    readable_dir = (root + directory).replace("\\", "/")
                    progress.log(
                        f":sparkles: Created directory: {readable_dir!r}"
                    )

                else:
                    with open(root + content['fn'], "wb") as file:
                        file.write(content['content'])

                    bytes_string = bytes_to_readable(len(content['content']))
                    readable_fn = (root + content['fn']).replace("\\", "/")
                    progress.log(
                        f"👉 Created & edited {readable_fn} [d white]({bytes_string})[/d white]"
                    )

                progress.update(task, advance=1)

    @staticmethod
    def convert_dict_to_list(
        data: Dict[str, Any],
        prefix: str = "", 
        result: Optional[list] = None
    ) -> List[Dict[str, str]]:
        """Converts a directory dictionary to valid contents data."""
        if result is None:
            result = []

        for key, value in data.items():
            if isinstance(value, str):
                result.append({
                    "fn": prefix + key,
                    "content": bytes(value, encoding="utf-8")
                })

            elif isinstance(value, dict):
                result.append({
                    "fn": f"?mk:{prefix}{key}"
                })
                Template.convert_dict_to_list(value, prefix + key + "/", result)

            elif value == Ellipsis:
                result.append({
                    "fn": f"?mk:{prefix}{key}"
                })

        return result
