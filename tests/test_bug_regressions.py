"""Regressionstests — bugfix-library-transfer Batch #22 (2026-06-21).

Geprüfte Patterns:
  D3 — subprocess.run ohne timeout (main_window.py pandoc-Aufruf)
"""
import unittest
from pathlib import Path

GUI_SRC = Path(__file__).parent.parent / "src" / "gui"
MAIN_WIN = GUI_SRC / "main_window.py"


class TestD3MainWindowPandoc(unittest.TestCase):
    def _src(self):
        return MAIN_WIN.read_text(encoding="utf-8")

    def test_pandoc_subprocess_has_timeout(self):
        src = self._src()
        pandoc_idx = src.find("'pandoc'")
        self.assertGreater(pandoc_idx, 0,
                           "main_window: pandoc-Aufruf nicht gefunden")
        block = src[pandoc_idx:pandoc_idx + 300]
        self.assertIn("timeout=", block,
                      "main_window: pandoc subprocess.run ohne timeout= — BUG-D3")


if __name__ == "__main__":
    unittest.main()
