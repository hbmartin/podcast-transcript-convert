from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger  # type: ignore[import-not-found]

from podcast_transcript_convert.converters import FILE_CONVERTERS, Converter
from podcast_transcript_convert.errors import UnknownFileTypeError

from .database import list_files_from_db
from .file_typing import FileType, identify_file_type, identify_file_types
from .file_utils import list_files


@dataclass(slots=True)
class ConversionSummary:
    """The outcome of a bulk_convert run.

    converted: (source, destination) pairs successfully written
        (or planned, when dry_run is True).
    skipped: (source, destination) pairs whose destination already
        existed and overwrite was False.
    failed: (source, error message) pairs that could not be converted.
    unknown: source files whose transcript format could not be identified.
    """

    converted: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    dry_run: bool = False


def _destination_path(
    file_path: str,
    destination_dir: str,
    source_root: str | None = None,
) -> Path:
    """Map a source file to a destination JSON path.

    When the source lives under source_root, its relative directory
    structure is mirrored to avoid name collisions. Otherwise (e.g. paths
    from a database) fall back to parent-directory-name/file-name.
    """
    path = Path(file_path)
    relative: Path | None = None
    if source_root is not None:
        try:
            relative = path.relative_to(source_root)
        except ValueError:
            relative = None
    if relative is None:
        parent_name = path.parent.name
        relative = Path(parent_name) / path.name if parent_name else Path(path.name)
    return Path(destination_dir) / relative.with_suffix(".json")


def _assign_destinations(
    file_paths: list[str],
    destination_dir: str,
    source_root: str | None,
) -> dict[str, Path]:
    """Assign each source a unique destination, deduplicating collisions."""
    taken: set[Path] = set()
    destinations: dict[str, Path] = {}
    for file_path in file_paths:
        destination = _destination_path(file_path, destination_dir, source_root)
        candidate = destination
        counter = 1
        while candidate in taken:
            candidate = destination.with_name(
                f"{destination.stem} ({counter}){destination.suffix}",
            )
            counter += 1
        taken.add(candidate)
        destinations[file_path] = candidate
    return destinations


def convert_file(
    origin_file: str | Path,
    destination_file: str | Path,
    metadata: dict | None = None,
) -> None:
    """Convert a single transcript file of any supported format to JSON.

    Raises UnknownFileTypeError when the format cannot be identified.
    """
    file_type = identify_file_type(str(origin_file))
    if file_type == FileType.UNKNOWN:
        raise UnknownFileTypeError(str(origin_file))

    converter = FILE_CONVERTERS[file_type]
    converter(origin_file, destination_file, metadata)


def _run_conversion(
    converter: Converter,
    file_path: str,
    destination: Path,
    metadata: dict | None,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    converter(file_path, str(destination), metadata)


def bulk_convert(
    transcript_path: str,
    destination_path: str,
    ignore: list[str] | None = None,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> ConversionSummary:
    """Convert every transcript under transcript_path to PodcastIndex JSON.

    transcript_path may be a directory of transcripts or an
    overcast-to-sqlite database (path ending in .db). Conversion errors are
    logged and collected per file rather than aborting the whole run.
    """
    ignore = ignore if ignore is not None else []
    source_root: str | None = None
    if transcript_path.endswith(".db"):
        file_paths, metadatas = list_files_from_db(transcript_path, ignore)
    else:
        metadatas = {}
        file_paths = list_files(directory=transcript_path, ignore=ignore)
        source_root = transcript_path

    grouped = identify_file_types(file_paths)
    for file_type in FILE_CONVERTERS:
        logger.info(f"Found {len(grouped[file_type])} {file_type.upper()} files")

    summary = ConversionSummary(dry_run=dry_run)
    summary.unknown = grouped[FileType.UNKNOWN]
    if summary.unknown:
        logger.warning(f"Unknown: {summary.unknown}")

    jobs: list[tuple[str, Converter]] = sorted(
        (
            (file_path, converter)
            for file_type, converter in FILE_CONVERTERS.items()
            for file_path in grouped[file_type]
        ),
        key=lambda job: job[0],
    )
    destinations = _assign_destinations(
        [file_path for file_path, _ in jobs],
        destination_path,
        source_root,
    )

    pending: list[tuple[str, Converter, Path]] = []
    for file_path, converter in jobs:
        destination = destinations[file_path]
        if destination.exists() and not overwrite:
            summary.skipped.append((file_path, str(destination)))
            continue
        pending.append((file_path, converter, destination))

    if dry_run:
        summary.converted = [
            (file_path, str(destination)) for file_path, _, destination in pending
        ]
        logger.info(
            f"Dry run: would convert {len(summary.converted)} files "
            f"({len(summary.skipped)} already converted)",
        )
        return summary

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                _run_conversion,
                converter,
                file_path,
                destination,
                metadatas.get(file_path),
            ): (file_path, destination)
            for file_path, converter, destination in pending
        }
        for future in as_completed(futures):
            file_path, destination = futures[future]
            try:
                future.result()
            except Exception as e:  # noqa: BLE001 - keep converting remaining files
                logger.error(f"Failed to convert {file_path}: {e}")
                summary.failed.append((file_path, str(e)))
            else:
                summary.converted.append((file_path, str(destination)))

    logger.info(
        f"Converted {len(summary.converted)} files, "
        f"skipped {len(summary.skipped)} existing, "
        f"{len(summary.failed)} failed, "
        f"{len(summary.unknown)} unknown",
    )
    return summary
