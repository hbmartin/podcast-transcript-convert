# podcast-transcript-convert

[![PyPI](https://img.shields.io/pypi/v/podcast-transcript-convert.svg)](https://pypi.org/project/podcast-transcript-convert/)
[![Lint and Test](https://github.com/hbmartin/podcast-transcript-convert/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/podcast-transcript-convert/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Types: ty + pyrefly](https://img.shields.io/badge/types-ty%20%2B%20pyrefly-261230.svg)](https://github.com/astral-sh/ty)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://pypi.org/project/podcast-transcript-convert/)
[![twitter](https://img.shields.io/badge/@hmartin-00aced.svg?logo=twitter&logoColor=black)](https://twitter.com/hmartin)

<img src=".idea/icon.svg" width="100" align="right">

Convert podcast transcripts from HTML, SRT, WebVtt, Podlove etc into [PodcastIndex JSON](https://github.com/Podcastindex-org/podcast-namespace/blob/main/transcripts/transcripts.md).

Requires Python 3.13 or later.

## Installation

It is recommended to use [pipx](https://pipx.pypa.io/stable/) or [uv](https://docs.astral.sh/uv/) to install and run the CLI tool. If you wish to use the library, you can install with `pip` instead.

```bash
brew install pipx
pipx install podcast-transcript-convert
# or: uv tool install podcast-transcript-convert
```

If you've already installed the package and wish to upgrade:

```bash
pipx upgrade podcast-transcript-convert
```

## Usage

Run the conversion app on your transcripts directory.

```bash
transcript2json transcripts/ converted/
```

You can then inspect the output JSON files in the `converted/` directory. The directory structure of `transcripts/` is mirrored in `converted/` so that files with the same name do not collide.

You can also convert a single file:

```bash
transcript2json "episode.srt" converted/
# or specify the output file name
transcript2json "episode.srt" episode.json
```

Or read transcript paths and episode metadata from an [overcast-to-sqlite](https://github.com/hbmartin/overcast-to-sqlite) database (episode and feed metadata is embedded in the output JSON):

```bash
transcript2json overcast.db converted/
```

### Options

| Flag | Description |
| --- | --- |
| `--ignore-file PATH` | File with one filename per line to skip. Defaults to `.transcriptignore` in the working directory, if present. |
| `--overwrite` | Re-convert files whose destination JSON already exists (they are skipped by default). |
| `--dry-run` | Report what would be converted without writing any files. |
| `--quiet` | Only log warnings and errors. |
| `--version` | Print the version and exit. |

Files that fail to convert are logged and skipped — a single malformed transcript will not abort a bulk run. The exit code is `0` on success and `1` when nothing could be converted.

## Library Usage

```python
from podcast_transcript_convert.convert import bulk_convert

summary = bulk_convert("transcripts_dir/", "converted_dir/")
print(f"{len(summary.converted)} converted, {len(summary.failed)} failed")
```

`bulk_convert` accepts optional `ignore` (list of filenames to skip), `overwrite`, and `dry_run` arguments and returns a `ConversionSummary` with `converted`, `skipped`, `failed`, and `unknown` file lists.

To convert a single file of any supported type:

```python
from podcast_transcript_convert.convert import convert_file

convert_file("episode.srt", "episode.json")
```

Individual file type converters are in the `converters` package. You can use them directly if you know the file type.

You can use `file_typing.identify_file_type(file)` to determine the file type of a transcript file, or `file_typing.identify_file_types(files)` to group a collection of paths by detected type.

## Development

Pull requests are very welcome! For major changes, please open an issue first to discuss what you would like to change.

This project uses [uv](https://docs.astral.sh/uv/) for dependency management, building, and publishing.

```bash
git clone git@github.com:hbmartin/podcast-transcript-convert.git
cd podcast-transcript-convert
uv sync
uv run pytest
# Replace with the actual path to your transcript files
uv run transcript2json ~/Downloads/overcast-to-sqlite/archive/transcripts converted/
```

### Code Quality

This project is linted and formatted with [ruff](https://docs.astral.sh/ruff/) and type checked with [ty](https://github.com/astral-sh/ty) and [pyrefly](https://pyrefly.org/).

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check podcast_transcript_convert
uv run pyrefly check
```

## Authors
- [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - harold.martin at gmail
- Icon courtesy of [Vecteezy.com](https://www.vecteezy.com)
