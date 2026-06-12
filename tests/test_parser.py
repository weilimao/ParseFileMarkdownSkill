import unittest
import tempfile
import os
from markitdown_skill import MarkItDownParser

class TestMarkItDownParser(unittest.TestCase):
    """
    Unit and integration tests for MarkItDownParser.
    """
    def setUp(self):
        self.parser = MarkItDownParser()
        self.temp_files = []

    def tearDown(self):
        for path in self.temp_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    def _create_temp_file(self, content, suffix) -> str:
        # Create a temporary file to parse
        mode = 'wb' if isinstance(content, bytes) else 'w'
        encoding = None if isinstance(content, bytes) else 'utf-8'
        
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, mode, encoding=encoding) as f:
            f.write(content)
        self.temp_files.append(path)
        return path

    def test_csv_parsing(self):
        csv_content = "Name,Age,Role\nAlice,30,Engineer\nBob,25,Designer"
        path = self._create_temp_file(csv_content, ".csv")
        
        result = self.parser.parse(path)
        self.assertIn("Name", result["content"])
        self.assertIn("Alice", result["content"])
        self.assertEqual(result["metadata"]["fileName"], os.path.basename(path))
        self.assertEqual(result["metadata"]["mimeType"], "text/csv")

    def test_json_parsing(self):
        json_content = '{"name": "MarkItDownSkill", "status": "active"}'
        path = self._create_temp_file(json_content, ".json")
        
        result = self.parser.parse(path)
        self.assertIn("MarkItDownSkill", result["content"])
        self.assertEqual(result["metadata"]["mimeType"], "application/json")

    def test_html_parsing(self):
        html_content = "<html><body><h1>Introduction</h1><p>MarkItDown is awesome.</p></body></html>"
        path = self._create_temp_file(html_content, ".html")
        
        result = self.parser.parse(path)
        self.assertIn("# Introduction", result["content"])
        self.assertIn("MarkItDown is awesome.", result["content"])

    def test_bytes_parsing(self):
        csv_bytes = b"Item,Count\nLaptop,5\nMonitor,12"
        result = self.parser.parse(csv_bytes, file_name="hardware.csv")
        
        self.assertIn("Item", result["content"])
        self.assertIn("Laptop", result["content"])
        self.assertEqual(result["metadata"]["fileName"], "hardware.csv")
        self.assertEqual(result["metadata"]["mimeType"], "text/csv")

if __name__ == "__main__":
    unittest.main()
