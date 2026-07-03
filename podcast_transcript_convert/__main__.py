import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from loguru import logger  # type: ignore[import-not-found]

from .convert import bulk_convert, convert_file
from .errors import TranscriptConversionError

DEFAULT_IGNORE_FILENAME = ".transcriptignore"


def _package_version() -> str:
    try:
        return version("podcast-transcript-convert")
    except PackageNotFoundError:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcript2json",
        description=(
            "Convert podcast transcripts (HTML, SRT, WebVTT, Podlove XML, JSON) "
            "into PodcastIndex JSON."
        ),
    )
    parser.add_argument(
        "source",
        help=(
            "A transcript file, a directory of transcripts, "
            "or an overcast-to-sqlite database (.db)"
        ),
    )
    parser.add_argument(
        "destination",
        help=("Output directory (or output file when converting a single transcript)"),
    )
    parser.add_argument(
        "--ignore-file",
        type=Path,
        default=None,
        help=(
            "File with one filename per line to skip "
            f"(default: {DEFAULT_IGNORE_FILENAME} in the working directory, if present)"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-convert files whose destination JSON already exists",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be converted without writing any files",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only log warnings and errors",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_package_version()}",
    )
    return parser


def _read_ignore_list(ignore_file: Path | None) -> list[str]:
    if ignore_file is None:
        default = Path.cwd() / DEFAULT_IGNORE_FILENAME
        if not default.exists():
            return []
        ignore_file = default
    return [
        line
        for line in ignore_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _convert_single_file(source: Path, destination: Path) -> int:
    if destination.is_dir() or destination.suffix == "":
        destination.mkdir(parents=True, exist_ok=True)
        destination = destination / (source.stem + ".json")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        convert_file(source, destination)
    except (TranscriptConversionError, OSError) as e:
        logger.error(f"Failed to convert {source}: {e}")
        return 1
    logger.info(f"Converted {source} -> {destination}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.quiet:
        logger.remove()
        logger.add(sys.stderr, level="WARNING")

    source = Path(args.source)
    if source.is_file() and source.suffix != ".db":
        return _convert_single_file(source, Path(args.destination))

    ignore_list = _read_ignore_list(args.ignore_file)
    Path(args.destination).mkdir(parents=True, exist_ok=True)

    summary = bulk_convert(
        transcript_path=args.source,
        destination_path=args.destination,
        ignore=ignore_list,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    if summary.failed and not summary.converted:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
