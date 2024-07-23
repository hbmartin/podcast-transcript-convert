import sys
from pathlib import Path

from loguru import logger  # type: ignore[import-not-found]

from .convert import bulk_convert


def main() -> None:
    if len(sys.argv) < 3:  # noqa: PLR2004
        logger.error(
            "Usage: transcript2json <source> <output> <opt. ignore file>",
        )
        sys.exit(1)

    transcript_ignore_path = Path.cwd() / ".transcriptignore"
    ignore_list = (
        (
            []
            if not transcript_ignore_path.exists()
            else transcript_ignore_path.read_text().split("\n")
        )
        if len(sys.argv) == 3  # noqa: PLR2004
        else Path(sys.argv[3]).read_text().split("\n")
    )

    if Path(sys.argv[1]).is_dir() and len(sys.argv) > 2:  # noqa: PLR2004
        destination = Path(sys.argv[2])
        if not destination.exists():
            destination.mkdir(parents=True, exist_ok=True)

    bulk_convert(
        transcript_path=sys.argv[1],
        destination_path=sys.argv[2],
        ignore=ignore_list,
    )


if __name__ == "__main__":
    main()
