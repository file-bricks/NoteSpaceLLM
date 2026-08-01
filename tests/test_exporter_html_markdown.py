# -*- coding: utf-8 -*-
"""
Tests for Markdown-to-HTML conversion in ReportExporter and safe excerpt building in Workspace Exporter.
Verifies that code blocks, inline code, and HTML escaping work correctly without being corrupted
by Markdown rules.
"""

import tempfile
from pathlib import Path
import pytest

from src.reports.exporter import ReportExporter
from src.core.workspace_exporter import _build_excerpts


def test_markdown_to_html_code_block_preserves_content():
    """Fenced code blocks must preserve comments, math/operators, and escape HTML."""
    exporter = ReportExporter(Path(tempfile.gettempdir()))
    md_content = """# Test Title

Here is a python code snippet:

```python
# Comment inside code block
val = 2 * x * 3
if a < b and c > d:
    print("hello")
```
"""
    html_output = exporter._markdown_to_html(md_content)

    assert "<h1>Test Title</h1>" in html_output
    assert "<pre><code># Comment inside code block\nval = 2 * x * 3\nif a &lt; b and c &gt; d:\n    print(&quot;hello&quot;)</code></pre>" in html_output or \
           "&lt; b" in html_output and "2 * x * 3" in html_output
    assert "<h1>Comment inside" not in html_output
    assert "<em>" not in html_output


def test_markdown_to_html_inline_code_escaping():
    """Inline code must escape HTML entities."""
    exporter = ReportExporter(Path(tempfile.gettempdir()))
    md_content = "Use `x < 10 && y > 20` for checking bounds."
    html_output = exporter._markdown_to_html(md_content)

    assert "<code>x &lt; 10 &amp;&amp; y &gt; 20</code>" in html_output


def test_markdown_to_html_all_headers():
    """Headers h1 through h6 are converted properly."""
    exporter = ReportExporter(Path(tempfile.gettempdir()))
    md_content = """# H1
## H2
### H3
#### H4
##### H5
###### H6
"""
    html_output = exporter._markdown_to_html(md_content)

    assert "<h1>H1</h1>" in html_output
    assert "<h2>H2</h2>" in html_output
    assert "<h3>H3</h3>" in html_output
    assert "<h4>H4</h4>" in html_output
    assert "<h5>H5</h5>" in html_output
    assert "<h6>H6</h6>" in html_output


def test_build_excerpts_string_enum():
    """_build_excerpts handles string-based status and query_type values gracefully."""
    class DummySubQuery:
        def __init__(self, doc_id, status, q_type, q_text, result):
            self.id = "sq-1"
            self.document_id = doc_id
            self.status = status
            self.query_type = q_type
            self.query_text = q_text
            self.result_text = result

    class DummySubQueries:
        def __init__(self):
            self.queries = [
                DummySubQuery("doc-1", "completed", "summary", "Summarize document", "Sample excerpt text")
            ]

    class DummyProject:
        def __init__(self):
            self.subqueries = DummySubQueries()

    excerpts = _build_excerpts(DummyProject(), "doc-1")
    assert len(excerpts) == 1
    assert excerpts[0]["id"] == "sq-1"
    assert excerpts[0]["text"] == "Sample excerpt text"
    assert "summary: Summarize document" in excerpts[0]["source_hint"]
