# tests/test_roundtrip_series.py
from pydantic import BaseModel
from ci.transparency.types import Series

def test_series_model_schema_is_sane():
    assert issubclass(Series, BaseModel)
    js = Series.model_json_schema()
    assert isinstance(js, dict)
    assert "title" in js
    assert "properties" in js and js["properties"]
    assert "type" in js and js["type"] == "object"
    assert "description" in js

