import os
import shutil
import tempfile
import time
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
from renameimage.__main__ import rename_files, get_exif_date, format_date_for_filename

class TestRenameImage(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def create_dummy_file(self, filename, mtime=None):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as f:
            f.write("dummy content")
        if mtime:
            os.utime(filepath, (mtime, mtime))
        return filepath

    def test_rename_no_exif(self):
        # Create a file with a specific modification time
        # 2023-01-01 12:00:00
        mtime = datetime(2023, 1, 1, 12, 0, 0).timestamp()
        filename = "test_image.jpg"
        self.create_dummy_file(filename, mtime)

        rename_files(self.test_dir)

        expected_filename = "2023-01-01-12-00-00.jpg"
        expected_path = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_path), f"File should be renamed to {expected_filename}")
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, filename)))

    def test_rename_dry_run(self):
        mtime = datetime(2023, 1, 1, 12, 0, 0).timestamp()
        filename = "test_image_dry.jpg"
        self.create_dummy_file(filename, mtime)

        rename_files(self.test_dir, dry_run=True)

        # File should NOT be renamed
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "2023-01-01-12-00-00.jpg")))

    @patch('renameimage.__main__.get_exif_date')
    def test_rename_with_exif(self, mock_get_exif):
        # Mock EXIF data
        mock_get_exif.return_value = "2022:12:25 10:30:00"

        filename = "test_exif.jpg"
        self.create_dummy_file(filename)

        rename_files(self.test_dir)

        expected_filename = "2022-12-25-10-30-00.jpg"
        expected_path = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_path))

    def test_recursive(self):
        subdir = os.path.join(self.test_dir, "subdir")
        os.mkdir(subdir)

        mtime = datetime(2023, 1, 1, 12, 0, 0).timestamp()
        filename = "test_recursive.jpg"
        filepath = os.path.join(subdir, filename)
        with open(filepath, 'w') as f:
            f.write("dummy")
        os.utime(filepath, (mtime, mtime))

        rename_files(self.test_dir, recursive=True)

        expected_filename = "2023-01-01-12-00-00.jpg"
        expected_path = os.path.join(subdir, expected_filename)

        self.assertTrue(os.path.exists(expected_path))

    def test_collision_handling(self):
        mtime = datetime(2023, 1, 1, 12, 0, 0).timestamp()

        # Create two files that would result in the same name
        file1 = "test1.jpg"
        file2 = "test2.jpg"

        self.create_dummy_file(file1, mtime)
        # Wait a bit or force mtime to be same (system dependent resolution, but explicit setting works)
        self.create_dummy_file(file2, mtime)

        rename_files(self.test_dir)

        expected1 = "2023-01-01-12-00-00.jpg"
        expected2 = "2023-01-01-12-00-00_1.jpg"

        path1 = os.path.join(self.test_dir, expected1)
        path2 = os.path.join(self.test_dir, expected2)

        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))

if __name__ == '__main__':
    unittest.main()
