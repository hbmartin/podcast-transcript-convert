# podcast-transcript-convert

[![PyPI](https://img.shields.io/pypi/v/podcast-transcript-convert.svg)](https://pypi.org/project/podcast-transcript-convert/)
[![Lint and Test](https://github.com/hbmartin/podcast-transcript-convert/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/podcast-transcript-tools/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/🐧️-black-000000.svg)](https://github.com/psf/black)
[![Checked with pytype](https://img.shields.io/badge/🦆-pytype-437f30.svg)](https://google.github.io/pytype/)
[![twitter](https://img.shields.io/badge/@hmartin-00aced.svg?logo=twitter&logoColor=black)](https://twitter.com/hmartin)

Convert podcast transcripts from HTML, SRT, WebVtt, Podlove etc into [PodcastIndex JSON](https://github.com/Podcastindex-org/podcast-namespace/blob/main/transcripts/transcripts.md).


## Installation

It is recommended to use [pipx](https://pipx.pypa.io/stable/) to install and run the CLI tool. If you wish to use the library, you can install with `pip` instead.

```bash
brew install pipx
pipx install podcast-transcript-convert
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
You can then inspect the output JSON files in the `converted/` directory.

## Library Usage
```python
from podcast_transcript_convert.convert import bulk_convert

bulk_convert("transctipts_dir/", "converted_dir/")
```

Individual file type converters are in the `converters` package. You can use them directly if you know the file type.

You can use `file_typing.identify_file_type(file)` to determine the file type of a transcript file.


## Development

Pull requests are very welcome! For major changes, please open an issue first to discuss what you would like to change.

```bash
git clone git@github.com:hbmartin/podcast-transcript-convert.git
cd podcast-transcript-convert
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Replace with the actual path to your transcript files
python -m podcast_transcript_convert ~/Downloads/overcast-to-sqlite/archive/transcripts converted/
```

### Code Formatting

This project is linted with [ruff](https://docs.astral.sh/ruff/) and uses [Black](https://github.com/ambv/black) code formatting.


## Authors
- [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - harold.martin at gmail
