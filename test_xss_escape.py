import pytest
from unittest.mock import MagicMock
import app

def test_html_escape_imported():
    assert hasattr(app, "html")
    assert hasattr(app.html, "escape")

def test_html_escape_works():
    assert app.html.escape("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
