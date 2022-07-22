import os
import re
from pathlib import Path


def get_cache_dir(file_name: str = None) -> str:
    """Gets the cache directory of `corona-info`.

    The cache directory is located in `~/.cache/corona-info`. This function will automatically create 
    the directories if necessary. If given a file name, it will directly return the path to the file 
    instead.
    
    Parameters
    ----------
    file_name: str, optional
        A string of the file's name.

    Returns
    -------
    str
        A string of the path of the cache directory.
    """

    cache_dir = Path(Path.home(), ".cache", "corona-info")
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)

    if file_name is not None:
        cache_dir = cache_dir / file_name

    return str(cache_dir)


def cache_file(file_name: str, content: str):
    """Caches the specified file at the app's cache directory, which is at `~/.cache/corona-info/`

    Parameters
    ----------
    file_name : str
        A string of the file's name.
    content : str
        A string of the content that will be written into the specified file.
    """
    path = os.path.join(get_cache_dir(), file_name)
    with open(path, "w") as file:
        file.write(content)


def get_file_content(file_path: str) -> str:
    """
    Gets the contents of the file at the given file path.

    Parameters
    ----------
    file_path: str
        A string of the path of the file.

    Returns
    -------
    str
        A string of the given file's contents.
    """
    with open(file_path, "r") as file:
        return file.read()


def is_float(text: str) -> bool:
    """Checks if the given string is a float.

    Parameters
    ----------
    text : str
        A string which may contain a float/decimal number.

    Returns
    -------
    bool
        A boolean of whether the given string is a float number or not.
    """
    match = re.match(r"^\d*\.\d*$", text)

    return bool(match)


def convert_to_num(text: str) -> int | float | str:
    """
    Converts a string into either an int or float, depending on the string given. Returns the original string if it
    is not a number.

    Parameters
    ----------
    text: str
        A string that may or may not be converted into int or float.

    Returns
    -------
    int | float | str
        An int or float if the given string is a number. A string of the original string.

    """
    result = text

    if not result:  # If empty string
        result = 0
    elif result.isdigit():
        result = int(result)
    elif is_float(result):
        result = float(result)

    return result


if __name__ == "__main__":
    get_cache_dir()
    print(is_float("1001947.86"))
