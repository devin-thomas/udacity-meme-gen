# Meme Generator

I built this project for Udacity's Large Python Codebases with Libraries course
in the Intermediate Python Nanodegree. It loads quotes from CSV, DOCX, PDF, and
TXT files, pairs them with local images, and generates captioned memes from both
a command-line interface and a Flask web app.

## Project Highlights

- I implemented a `QuoteEngine` package with an abstract ingestor interface and
  separate CSV, DOCX, PDF, and TXT strategy classes.
- I added recursive quote and image discovery with curated runtime pools, so
  ingestion fixtures never leak into generated memes.
- I used Pillow in `MemeEngine` to resize images, measure and wrap captions,
  choose a quiet randomized location, and save generated JPEG files.
- I completed the Udacity CLI and Flask starter code, including user-submitted
  image URLs through `requests`.
- I added custom exceptions, focused pytest coverage, original quote content,
  deploy-ready metadata, and a polished web interface.

## Tech Stack

- Python 3.12+
- Flask and gunicorn for the web app
- Pillow for image processing
- pandas for CSV ingestion
- python-docx for DOCX ingestion
- `pdftotext` through `subprocess` for PDF ingestion, with `pypdf` as a local
  fallback when the CLI is not installed
- pytest for focused unit tests

## Getting Started

Create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Command-Line Usage

Generate a random meme:

```powershell
.\.venv\Scripts\python.exe meme.py
```

Generate a meme from a specific image and quote:

```powershell
.\.venv\Scripts\python.exe meme.py `
  --path _data\photos\dog\xander_1.jpg `
  --body "Readable code is a kindness to tomorrow me." `
  --author Devin
```

The command prints the generated image path in `tmp/`.

### PDF parser selection

`PDFIngestor` first checks the `PDFTOTEXT_PATH` environment variable for an
explicit `pdftotext` executable, then searches the system `PATH`. If neither
location provides the CLI, it automatically falls back to the installed
`pypdf` library. For example, on Windows:

```powershell
$env:PDFTOTEXT_PATH = "C:\Program Files\xpdf\bin64\pdftotext.exe"
```

## Web App Usage

Start the Flask app:

```powershell
.\.venv\Scripts\python.exe app.py
```

Then open `http://127.0.0.1:5000`.

For deployment-style runs, I included a `Procfile`:

```powershell
gunicorn app:app
```

Generated web images are written to `static/generated/`, which is intentionally
ignored by git.

## Module Guide

### `QuoteEngine`

I use `QuoteModel` to store a quote body and author, and I print it as
`"body" - author`. `IngestorInterface` defines the shared contract for
`can_ingest` and `parse`, plus the common quote-line parser. `TextIngestor`,
`CSVIngestor`, `DocxIngestor`, and `PDFIngestor` each handle one file type.
`Ingestor` is the facade I use from the app and CLI.

Example:

```python
from QuoteEngine import Ingestor

quotes = Ingestor.parse("_data/DogQuotes/DogQuotesTXT.txt")
```

### `MemeEngine`

I use `MemeEngine` to load a JPEG or PNG from disk, resize it to a maximum width
of 500 pixels, and save the generated meme. Before drawing, I measure each line,
fit the caption to the image, and rank a grid of possible locations by visual
detail. I randomly choose between the two quietest regions, which keeps the
rubric-required variation while reducing clipped text and covered faces.

Example:

```python
from MemeEngine import MemeEngine

engine = MemeEngine("tmp")
path = engine.make_meme("_data/photos/dog/xander_1.jpg", "Hello", "Devin")
```

### `meme_resources.py`

I keep shared resource discovery here so the CLI and Flask app load the same
curated content. Runtime quotes come from `_data/DogQuotes` and
`_data/PortfolioQuotes`, with duplicate body-author pairs removed in source
order. Runtime images come from `_data/photos/dog`. I keep `_data/SimpleLines`
as a multi-format ingestion fixture and the abstract original images as design
experiments, but I intentionally exclude both from random meme generation.

### `meme.py`, `main.py`, and `app.py`

`meme.py` is the command-line entry point. `main.py` is a thin compatibility
wrapper for rubric checks that expect that filename. `app.py` serves the Flask
app and downloads submitted image URLs into a temporary file before generating
the meme.

## Repository Structure

```text
.
├── MemeEngine/              # Pillow image captioning package
├── QuoteEngine/             # Quote ingestion package and strategy classes
├── _data/                   # Starter data plus my original quote/image content
├── static/                  # CSS and generated web output folder
├── templates/               # Flask templates
├── tests/                   # Focused pytest coverage
├── app.py                   # Flask entry point
├── meme.py                  # CLI entry point
├── main.py                  # Compatibility CLI wrapper
├── meme_resources.py        # Shared resource discovery
├── Procfile                 # Deployment command
└── requirements.txt         # Python dependencies
```

## Validation

I validate the project with:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe meme.py --path _data\photos\dog\xander_1.jpg --body "Portfolio ready" --author Devin
```

## Reflection

I kept the file parsers small and pushed shared behavior into the abstract base
class so the strategy pattern stays visible without duplicating parsing logic.
The extra directory discovery and PDF fallback make the app easier to run as a
portfolio project, while the tests stay focused on the behaviors most likely to
break: quote parsing, unsupported files, runtime content curation, CLI
validation, caption bounds, placement quality, and image generation.
