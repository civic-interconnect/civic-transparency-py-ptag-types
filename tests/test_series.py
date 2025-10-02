# tests/test_series.py
from importlib.resources import files

from ci.transparency.ptag.types import PTagSeries
from pydantic import BaseModel

# Access schemas using string path (no import needed)
schema_dir = files("ci.transparency.ptag.spec.schemas")
ptag_series_json = schema_dir.joinpath("ptag_series.schema.json").read_text(encoding="utf-8")


def test_series_model_schema_is_sane():
    assert issubclass(PTagSeries, BaseModel)
    js = PTagSeries.model_json_schema()
    assert isinstance(js, dict)
    assert "title" in js
    assert "properties" in js and js["properties"]
    assert "type" in js and js["type"] == "object"


def test_points_can_be_empty():
    PTagSeries.model_validate(
        {
            "topic": "#X",
            "generated_at": "2025-01-01T00:00:00Z",
            "interval": "minute",
            "points": [],
        }
    )
