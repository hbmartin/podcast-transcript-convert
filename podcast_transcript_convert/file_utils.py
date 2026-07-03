from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def _is_file_allowed(filename: str, ignore: list[str]) -> bool:
    return (
        filename not in ignore
        and not filename.startswith(".")
        and not filename.endswith(".pdf")
        and not filename.endswith(".octet-stream")
    )


def list_files(directory: str, ignore: list[str]) -> list[str]:
    file_paths: list[str] = []  # List to store file paths
    for root, _, filenames in Path(directory).walk():
        file_paths.extend(
            str(root / filename)
            for filename in filenames
            if _is_file_allowed(filename, ignore)
        )
    return file_paths


def read_text_robust(file_path: str | Path) -> str:
    """Read a text file as UTF-8 (BOM tolerant), replacing undecodable bytes.

    Real-world transcript files are not always valid UTF-8; rather than
    crashing on the first bad byte, fall back to replacement characters.
    """
    path = Path(file_path)
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text_utf8(file_path: str | Path, data: str) -> None:
    """Write a text file as UTF-8 regardless of platform default encoding."""
    Path(file_path).write_text(data=data, encoding="utf-8")


def _read_first_line(file_path: str) -> str:
    path = Path(file_path)
    try:
        with path.open(encoding="utf-8-sig") as file:
            return file.readline()
    except UnicodeDecodeError:
        with path.open(encoding="utf-8-sig", errors="replace") as file:
            return file.readline()


def map_files_in_parallel[T](
    file_paths: list[str],
    transform: Callable[[str], T],
) -> list[tuple[str, T]]:
    """Apply transform to each file path concurrently.

    Returns (file_path, result) tuples in input order.
    """
    with ThreadPoolExecutor() as executor:
        results = executor.map(transform, file_paths)
        return list(zip(file_paths, results, strict=True))
