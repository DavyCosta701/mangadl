# MangaDex Downloader

A command-line tool that helps you download manga from MangaDex. This tool makes it easy to search for and download manga chapters directly from the terminal.

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

After installation, you can run the application from anywhere on your system:

```powershell
mangadl
```

To check the version:
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

