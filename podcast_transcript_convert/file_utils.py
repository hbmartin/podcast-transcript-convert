from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from os import walk
from pathlib import Path
from typing import TypeVar


def _is_file_allowed(filename: str, ignore: list[str]) -> bool:
    return (
        filename not in ignore
        and not filename.startswith(".")
        and not filename.endswith(".pdf")
        and not filename.endswith(".octet-stream")
    )


def list_files(directory: str, ignore: list[str]) -> list[str]:
    file_paths: list[str] = []  # List to store file paths
    for root, _, filenames in walk(directory):
        dirpath = Path(root)
        file_paths.extend(
            str(dirpath / filename)
            for filename in filenames
            if _is_file_allowed(filename, ignore)
        )
    return file_paths


def _read_first_line(file_path: str) -> str:
    try:
        with Path(file_path).open() as file:
            return file.readline()
    except ValueError as e:
        e.add_note(file_path)
        raise


T = TypeVar("T")


def _read_files_in_parallel(
    file_paths: list[str],
    transform: Callable[[str], T],
) -> list[tuple[str, T]]:
    def _read_and_transform(file_path: str) -> tuple[str, T]:
        return file_path, transform(_read_first_line(file_path))

    with ThreadPoolExecutor() as executor:
        # Mapping the read_first_line function over all file paths
        results = executor.map(_read_and_transform, file_paths)
        return list(results)
