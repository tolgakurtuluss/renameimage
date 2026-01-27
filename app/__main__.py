import os
import logging
from datetime import datetime
from typing import Optional, List
import exifread
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS: List[str] = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".tif",
    ".ico",
    ".webp",
    ".heic",
    ".heif",
    ".jfif",
]


def get_exif_date(file_path: str) -> Optional[str]:
    """Extract date from EXIF data."""
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f)
            if "EXIF DateTimeOriginal" in tags:
                return str(tags["EXIF DateTimeOriginal"])
    except Exception:
        # If there's an error reading the file or EXIF, return None
        return None
    return None


def get_file_date(file_path: str) -> datetime:
    """Get the file's modification time."""
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def format_date_for_filename(date_str: str) -> str:
    """Convert date string to yyyy-mm-dd-hh-mm-ss format."""
    date_format = "%Y:%m:%d %H:%M:%S"
    dt = datetime.strptime(date_str, date_format)
    return dt.strftime("%Y-%m-%d-%H-%M-%S")


def process_file(
    filepath: str, dry_run: bool = False
) -> None:
    """Process a single file: calculate new name and rename if not dry_run."""
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    if not any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
        return

    exif_date = get_exif_date(filepath)
    if exif_date:
        try:
            new_date_str = format_date_for_filename(exif_date)
        except ValueError:
            # Fallback if EXIF date format is unexpected
            mod_date = get_file_date(filepath)
            new_date_str = mod_date.strftime("%Y-%m-%d-%H-%M-%S")
    else:
        # If no EXIF data, use file modification time
        mod_date = get_file_date(filepath)
        new_date_str = mod_date.strftime("%Y-%m-%d-%H-%M-%S")

    # Create new filename preserving extension
    file_extension = os.path.splitext(filename)[1]
    new_filename = f"{new_date_str}{file_extension}"
    new_path = os.path.join(directory, new_filename)

    # Avoid overwriting existing files
    counter = 1
    while os.path.exists(new_path) and new_path != filepath:
        new_path = os.path.join(
            directory, f"{new_date_str}_{counter}{file_extension}"
        )
        counter += 1

    if filepath != new_path:
        logger.info(f'Renaming "{filename}" to "{os.path.basename(new_path)}"')
        if not dry_run:
            try:
                os.rename(filepath, new_path)
            except OSError as e:
                logger.error(f"Error renaming {filename}: {e}")


def rename_files(directory: str, dry_run: bool = False, recursive: bool = False) -> None:
    """Rename image files in the specified directory."""
    if not os.path.isdir(directory):
        logger.error(f"Error: Directory '{directory}' not found.")
        return

    if recursive:
        for root, _, files in os.walk(directory):
            for filename in files:
                process_file(os.path.join(root, filename), dry_run)
    else:
        for filename in os.listdir(directory):
            process_file(os.path.join(directory, filename), dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename image files based on EXIF data."
    )
    parser.add_argument("directory", help="Directory containing image files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate renaming without moving files",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively process subdirectories",
    )

    args = parser.parse_args()
    rename_files(args.directory, dry_run=args.dry_run, recursive=args.recursive)
