# tests/test_imports.py
from importlib.resources import files

from ci.transparency.ptag.types import PTagSeries, PTag
# Access schemas using string path (no import needed)
schema_dir = files("ci.transparency.ptag.spec.schemas")
ptag_json = schema_dir.joinpath("ptag.schema.json").read_text(encoding="utf-8")
ptag_series_json = schema_dir.joinpath("ptag_series.schema.json").read_text(encoding="utf-8")

def test_imports():  # just proves modules exist
    assert PTagSeries and PTag
