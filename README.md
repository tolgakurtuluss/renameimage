# renameimage

`renameimage` is a Python tool that renames image files in a specified directory to the format `yyyy-mm-dd-hh-mm-ss` based on their EXIF DateTimeOriginal data or file modification time.

## Features

- **Metadata-based Renaming**: Uses EXIF data if available; falls back to file modification time.
- **Recursive Processing**: Can process images in subdirectories using the `-r` or `--recursive` flag.
- **Dry Run**: Preview changes without modifying files using the `--dry-run` flag.
- **Safe**: Preserves file extensions and prevents overwriting existing files by appending a counter.
- **Supported Formats**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.ico`, `.webp`, `.heic`, `.heif`, `.jfif`.

## Requirements

- Python 3.7+
- `exifread`

## Installation

1. Clone this repository.
2. Install dependencies (it is recommended to use a virtual environment):

```bash
pip install .
```

## Usage

After installation, run the module:

```bash
python -m renameimage [directory] [options]
```

Or run directly from source without installation:

```bash
python -m src.renameimage [directory] [options]
```

### Arguments

- `directory`: The directory containing the images to rename.

### Options

- `--dry-run`: Simulate the renaming process without moving any files.
- `-r`, `--recursive`: Recursively process subdirectories.

### Examples

Rename images in a folder:
```bash
python -m renameimage /path/to/photos
```

Preview changes (dry run):
```bash
python -m renameimage /path/to/photos --dry-run
```

Recursively rename images:
```bash
python -m renameimage /path/to/photos -r
```
