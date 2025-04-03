from typing import Any, List, Union
from collections.abc import Hashable
import os

def removeDuplicatesHashable(data: List[Any]):
    new_data = []
    [new_data.append(n) for n in data if n not in new_data]
    return new_data

def listToFilter(title: str, ext: List[str]):
    """Convert a list of extensions into a name filter for file dialogs."""
    if len(ext) == 0:
        return f"All Files (*)"
    
    last_idx = len(ext) - 1

    output = f"{title} ("
    for i in range(last_idx):
        output += f"*.{ext[i]} "

    output += f"*.{ext[last_idx]})" # Last one (no space at the end)
    return output

def isRunningInFlatpak() -> bool:
    """Determines if the application is running inside a Flatpak sandbox."""
    if os.environ.get("FLATPAK_ID", None) is not None:
        return True
    
    return False