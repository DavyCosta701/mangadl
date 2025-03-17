# MangaDex Downloader

A command-line tool that helps you download manga from MangaDex. This tool makes it easy to download manga chapters directly from the terminal.

## Installation

You can install MangaDex Downloader directly from GitHub using pipx with uv:

```powershell
# Replace YOUR_USERNAME with the GitHub username
pipx install git+https://github.com/DavyCosta701/mangadl.git --pip uv
```

### Prerequisites

- Python 3.6 or higher
- pipx
- uv

## Usage

### Basic Usage

Download manga chapters with default settings:

```powershell
mangadl download "https://mangadex.org/title/your-manga-id"
```

### Advanced Options

For now, the mangadl only allows the download from the mangadex website:

```powershell
mangadl mangadex_dl download [OPTIONS] URL

Options:
  --language TEXT     Language code for the manga chapters (e.g., pt-br, en)
                     [default: pt-br]
  --output-dir TEXT  Directory to save the downloaded manga
                     [default: output]
  --max-retries INTEGER  Maximum number of retry attempts for failed downloads
                        [default: 3]
  --help            Show this message and exit.
```

### Examples

1. Download manga in English:
```powershell
mangadl download "https://mangadex.org/title/your-manga-id" --language en
```

2. Specify custom output directory:
```powershell
mangadl download "https://mangadex.org/title/your-manga-id" --output-dir my-manga
```

3. Set maximum retry attempts:
```powershell
mangadl download "https://mangadex.org/title/your-manga-id" --max-retries 5
```

### Features

- Downloads all available chapters in the specified language
- Automatically converts chapters to PDF format
- Supports parallel downloading (up to 10 chapters simultaneously)
- Includes retry mechanism for failed downloads
- Shows progress bars for overall download and individual chapters
- Creates organized output with one PDF per chapter

### Version Information

To check the version of the downloader:

```powershell
mangadl version
```

## Updating

When updates are available, you can upgrade your installation with:

```powershell
pipx upgrade mangadl
```

## Development

If you want to contribute to this project:

1. **Clone the repository**
   ```powershell
   git clone https://github.com/YOUR_USERNAME/mangadl.git
   cd mangadl
   ```

2. **Set up a virtual environment**
   ```powershell
   uv venv
   ```

3. **Install dependencies**
   ```powershell
   uv pip install -e .
   ```

4. **Make your changes and commit them**
   ```powershell
   git add .
   git commit -m "Description of changes"
   git push
   ```