"""Tests for the toolbox utilities module."""
import os
import sys
import tempfile
import time
import unittest
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.toolbox import (
    gen_time_str,
    get_log_folder,
    get_upload_folder,
    write_history_to_file,
    find_free_port,
    find_recent_files,
    zip_folder,
    trimmed_format_exc,
    trimmed_format_exc_markdown,
    regular_txt_to_markdown,
    clear_line_break,
    DummyWith,
    ProxyNetworkActivate,
    get_pictures_list,
    encode_image_base64,
    check_packages,
    map_file_to_sha256,
    Singleton,
)


class TestGenTimeStr(unittest.TestCase):
    """Test cases for gen_time_str."""

    def test_format_correct(self):
        """Test that timestamp has correct format."""
        result = gen_time_str()
        # Format: YYYY-MM-DD-HH-MM-SS
        parts = result.split("-")
        self.assertEqual(len(parts), 6)
        self.assertEqual(len(parts[0]), 4)  # Year
        self.assertEqual(len(parts[1]), 2)  # Month
        self.assertEqual(len(parts[2]), 2)  # Day
        self.assertEqual(len(parts[3]), 2)  # Hour
        self.assertEqual(len(parts[4]), 2)  # Minute
        self.assertEqual(len(parts[5]), 2)  # Second

    def test_returns_string(self):
        """Test that result is a string."""
        result = gen_time_str()
        self.assertIsInstance(result, str)


class TestGetLogFolder(unittest.TestCase):
    """Test cases for get_log_folder."""

    def test_returns_path(self):
        """Test that get_log_folder returns a path string."""
        result = get_log_folder()
        self.assertIsInstance(result, str)

    def test_creates_directory(self):
        """Test that the directory is created if it doesn't exist."""
        result = get_log_folder(user="test_user", plugin_name="test_plugin")
        self.assertTrue(os.path.exists(result))
        # Cleanup
        if os.path.exists(result):
            shutil.rmtree(os.path.dirname(result))

    def test_user_specific_path(self):
        """Test that user is included in path."""
        result = get_log_folder(user="specific_user")
        self.assertIn("specific_user", result)


class TestGetUploadFolder(unittest.TestCase):
    """Test cases for get_upload_folder."""

    def test_returns_path(self):
        """Test that get_upload_folder returns a path string."""
        result = get_upload_folder()
        self.assertIsInstance(result, str)

    def test_with_tag(self):
        """Test that tag is included in path."""
        result = get_upload_folder(tag="2024-01-01-12-00-00")
        self.assertIn("2024-01-01-12-00-00", result)


class TestWriteHistoryToFile(unittest.TestCase):
    """Test cases for write_history_to_file."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_writes_file(self):
        """Test that history is written to file."""
        history = ["User question", "Assistant answer"]
        file_path = os.path.join(self.temp_dir, "test.md")
        result = write_history_to_file(history, file_fullname=file_path)
        self.assertTrue(os.path.exists(result))

    def test_file_contains_history(self):
        """Test that file contains the history content."""
        history = ["What is Python?", "Python is a programming language."]
        file_path = os.path.join(self.temp_dir, "test.md")
        write_history_to_file(history, file_fullname=file_path)
        with open(file_path, "r") as f:
            content = f.read()
        self.assertIn("What is Python?", content)
        self.assertIn("Python is a programming language.", content)

    def test_auto_caption(self):
        """Test that auto_caption adds ## to user messages."""
        history = ["Question", "Answer"]
        file_path = os.path.join(self.temp_dir, "test.md")
        write_history_to_file(history, file_fullname=file_path, auto_caption=True)
        with open(file_path, "r") as f:
            content = f.read()
        self.assertIn("## Question", content)

    def test_returns_absolute_path(self):
        """Test that result is an absolute path."""
        history = ["Q", "A"]
        file_path = os.path.join(self.temp_dir, "test.md")
        result = write_history_to_file(history, file_fullname=file_path)
        self.assertTrue(os.path.isabs(result))


class TestFindFreePort(unittest.TestCase):
    """Test cases for find_free_port."""

    def test_returns_integer(self):
        """Test that a port number is returned."""
        result = find_free_port()
        self.assertIsInstance(result, int)

    def test_port_in_valid_range(self):
        """Test that port is in valid range."""
        result = find_free_port()
        self.assertGreater(result, 0)
        self.assertLess(result, 65536)


class TestFindRecentFiles(unittest.TestCase):
    """Test cases for find_recent_files."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_finds_recent_file(self):
        """Test finding recently created files."""
        # Create a file
        file_path = os.path.join(self.temp_dir, "recent.txt")
        with open(file_path, "w") as f:
            f.write("test")
        result = find_recent_files(self.temp_dir, seconds=60)
        self.assertIn(file_path, result)

    def test_ignores_directories(self):
        """Test that directories are not included."""
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)
        result = find_recent_files(self.temp_dir)
        self.assertNotIn(subdir, result)

    def test_ignores_log_files(self):
        """Test that .log files are ignored."""
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, "w") as f:
            f.write("log")
        result = find_recent_files(self.temp_dir)
        self.assertNotIn(log_file, result)

    def test_empty_directory(self):
        """Test with empty directory."""
        result = find_recent_files(self.temp_dir)
        self.assertEqual(result, [])


class TestZipFolder(unittest.TestCase):
    """Test cases for zip_folder."""

    def setUp(self):
        """Set up test fixtures."""
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        # Create some files
        with open(os.path.join(self.source_dir, "test.txt"), "w") as f:
            f.write("test content")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.dest_dir)

    def test_creates_zip(self):
        """Test that zip file is created."""
        result = zip_folder(self.source_dir, self.dest_dir, "test.zip")
        self.assertTrue(os.path.exists(result))

    def test_zip_contains_files(self):
        """Test that zip contains the source files."""
        import zipfile
        zip_path = zip_folder(self.source_dir, self.dest_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = z.namelist()
        self.assertIn("test.txt", names)

    def test_nonexistent_source_returns_none(self):
        """Test that nonexistent source returns None."""
        result = zip_folder("/nonexistent/path", self.dest_dir, "test.zip")
        self.assertIsNone(result)


class TestTrimmedFormatExc(unittest.TestCase):
    """Test cases for trimmed_format_exc."""

    def test_returns_string(self):
        """Test that result is a string."""
        try:
            raise ValueError("test error")
        except:
            result = trimmed_format_exc()
        self.assertIsInstance(result, str)

    def test_contains_error_info(self):
        """Test that result contains error information."""
        try:
            raise ValueError("specific error message")
        except:
            result = trimmed_format_exc()
        self.assertIn("ValueError", result)
        self.assertIn("specific error message", result)


class TestTrimmedFormatExcMarkdown(unittest.TestCase):
    """Test cases for trimmed_format_exc_markdown."""

    def test_wrapped_in_code_block(self):
        """Test that result is wrapped in markdown code block."""
        try:
            raise ValueError("test")
        except:
            result = trimmed_format_exc_markdown()
        self.assertTrue(result.startswith("\n\n```\n"))
        self.assertTrue(result.endswith("```"))


class TestRegularTxtToMarkdown(unittest.TestCase):
    """Test cases for regular_txt_to_markdown."""

    def test_adds_double_newlines(self):
        """Test that single newlines become double."""
        result = regular_txt_to_markdown("line1\nline2")
        self.assertIn("\n\n", result)

    def test_handles_none(self):
        """Test that None returns empty string."""
        result = regular_txt_to_markdown(None)
        self.assertEqual(result, "")

    def test_no_triple_newlines(self):
        """Test that triple newlines are collapsed."""
        result = regular_txt_to_markdown("line1\n\nline2")
        self.assertNotIn("\n\n\n", result)


class TestClearLineBreak(unittest.TestCase):
    """Test cases for clear_line_break."""

    def test_removes_newlines(self):
        """Test that newlines are replaced with spaces."""
        result = clear_line_break("line1\nline2")
        self.assertEqual(result, "line1 line2")

    def test_handles_none(self):
        """Test that None returns None."""
        result = clear_line_break(None)
        self.assertIsNone(result)

    def test_collapses_double_spaces(self):
        """Test that double spaces are collapsed."""
        result = clear_line_break("word1  word2")
        self.assertEqual(result, "word1 word2")


class TestDummyWith(unittest.TestCase):
    """Test cases for DummyWith context manager."""

    def test_can_be_used_as_context_manager(self):
        """Test that DummyWith works as context manager."""
        with DummyWith() as d:
            self.assertIsInstance(d, DummyWith)

    def test_does_not_suppress_exceptions(self):
        """Test that exceptions are not suppressed."""
        with self.assertRaises(ValueError):
            with DummyWith():
                raise ValueError("test")


class TestProxyNetworkActivate(unittest.TestCase):
    """Test cases for ProxyNetworkActivate context manager."""

    def setUp(self):
        """Save original environment."""
        self.original_http = os.environ.get("HTTP_PROXY")
        self.original_https = os.environ.get("HTTPS_PROXY")
        self.original_no_proxy = os.environ.get("no_proxy")

    def tearDown(self):
        """Restore original environment."""
        if self.original_http:
            os.environ["HTTP_PROXY"] = self.original_http
        elif "HTTP_PROXY" in os.environ:
            del os.environ["HTTP_PROXY"]

        if self.original_https:
            os.environ["HTTPS_PROXY"] = self.original_https
        elif "HTTPS_PROXY" in os.environ:
            del os.environ["HTTPS_PROXY"]

        if self.original_no_proxy:
            os.environ["no_proxy"] = self.original_no_proxy
        elif "no_proxy" in os.environ:
            del os.environ["no_proxy"]

    def test_can_be_used_as_context_manager(self):
        """Test that ProxyNetworkActivate works as context manager."""
        with ProxyNetworkActivate() as p:
            self.assertIsInstance(p, ProxyNetworkActivate)

    def test_clears_proxy_on_exit(self):
        """Test that proxy environment variables are cleared on exit."""
        with ProxyNetworkActivate():
            pass
        self.assertEqual(os.environ.get("no_proxy"), "*")


class TestGetPicturesList(unittest.TestCase):
    """Test cases for get_pictures_list."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_finds_jpg_files(self):
        """Test finding jpg files."""
        jpg_file = os.path.join(self.temp_dir, "test.jpg")
        with open(jpg_file, "wb") as f:
            f.write(b"fake jpg")
        result = get_pictures_list(self.temp_dir)
        self.assertIn(jpg_file, result)

    def test_finds_png_files(self):
        """Test finding png files."""
        png_file = os.path.join(self.temp_dir, "test.png")
        with open(png_file, "wb") as f:
            f.write(b"fake png")
        result = get_pictures_list(self.temp_dir)
        self.assertIn(png_file, result)

    def test_nonexistent_path_returns_empty(self):
        """Test that nonexistent path returns empty list."""
        result = get_pictures_list("/nonexistent/path")
        self.assertEqual(result, [])


class TestEncodeImageBase64(unittest.TestCase):
    """Test cases for encode_image_base64."""

    def test_encodes_file(self):
        """Test encoding a file to base64."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        try:
            result = encode_image_base64(temp_path)
            self.assertIsInstance(result, str)
            # Base64 of "test content"
            import base64
            expected = base64.b64encode(b"test content").decode("utf-8")
            self.assertEqual(result, expected)
        finally:
            os.unlink(temp_path)


class TestCheckPackages(unittest.TestCase):
    """Test cases for check_packages."""

    def test_existing_package_passes(self):
        """Test that existing package doesn't raise."""
        check_packages(["os", "sys"])

    def test_nonexistent_package_raises(self):
        """Test that nonexistent package raises ModuleNotFoundError."""
        with self.assertRaises(ModuleNotFoundError):
            check_packages(["nonexistent_package_xyz"])


class TestMapFileToSha256(unittest.TestCase):
    """Test cases for map_file_to_sha256."""

    def test_returns_hash_string(self):
        """Test that a hash string is returned."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        try:
            result = map_file_to_sha256(temp_path)
            self.assertIsInstance(result, str)
            self.assertEqual(len(result), 64)  # SHA-256 produces 64 hex chars
        finally:
            os.unlink(temp_path)


class TestSingleton(unittest.TestCase):
    """Test cases for Singleton decorator."""

    def test_creates_single_instance(self):
        """Test that only one instance is created."""
        @Singleton
        class TestClass:
            def __init__(self, value):
                self.value = value

        instance1 = TestClass(1)
        instance2 = TestClass(2)
        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, 1)  # First value is preserved


if __name__ == '__main__':
    unittest.main()
