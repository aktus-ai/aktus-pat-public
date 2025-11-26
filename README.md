# Aktus Data Pipeline

Command-line and UI interface for the Aktus Data Pipeline API.

## Installation

```bash
pip install requests
```

## Usage

**CLI:**
```bash
python aktus_cli.py [--base-url URL] [--compact] [--quiet] COMMAND [ARGS]
```

**UI:**
```bash
python aktus_ui.py
```

## Commands

### CLI

1. **Login** - `python aktus_cli.py login <api_key>`
2. **Logout** - `python aktus_cli.py logout`
3. **Upload** - `python aktus_cli.py upload <file.pdf> [--provider NAME]`
4. **List** - `python aktus_cli.py list [--skip N] [--limit N]`
5. **Portfolios** - `python aktus_cli.py portfolios <filename>`

### UI

Interactive menu with numbered options (1-6):
- Login, Logout, Upload, List, Portfolios
- **Batch Upload** (#6) - Upload multiple PDFs from a directory

## Batch Upload

Process multiple files at once:

```bash
python batch_upload.py <directory> [--provider NAME]
```

Example: `python batch_upload.py ./documents --provider "Provider Name"`

## Options

| Option | Description |
|--------|-------------|
| `--base-url URL` | API server URL (default: `https://pat.aktus.ai`) |
| `--compact` | Compact JSON output |
| `--quiet` | Minimal output (filenames/names only) |

Session persists in `~/.aktus_session` after login.
