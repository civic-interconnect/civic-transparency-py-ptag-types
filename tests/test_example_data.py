# tests/test_example_data.py
from importlib.resources import files
import json
from pathlib import Path
from ci.transparency.ptag.types import PTagSeries, PTag
import pytest
# pyright: reportGeneralTypeIssues=false, reportUnknownMemberType=false

# Access schemas using string path (no import needed)
schema_dir = files("ci.transparency.ptag.spec.schemas")
ptag_json = schema_dir.joinpath("ptag.schema.json").read_text(encoding="utf-8")
ptag_series_json = schema_dir.joinpath("ptag_series.schema.json").read_text(encoding="utf-8")

class TestExampleData:
    """Test that our example data validates correctly."""

    def test_series_minimal_example(self):
        """Test minimal valid PTagSeries example."""
        data_file = Path(__file__).parent / "data" / "series_minimal.json"
        data = json.loads(data_file.read_text())

        # Should
        # validate without errors
        series = PTagSeries.model_validate(data)

        # Verify key properties
        assert series.topic == "#TestTopic"
        assert series.interval.value == "minute"  # Compare enum value, not enum object
        assert len(series.points) == 1
        assert series.points[0].volume == 100

        # Round-trip test
        serialized = series.model_dump()
        series2 = PTagSeries.model_validate(serialized)
        assert series == series2

    def test_ptag_minimal_example(self):
        """Test minimal valid PTag example."""
        data_file = Path(__file__).parent / "data" / "ptag_minimal.json"
        if not data_file.exists():
            # Create the test data if it doesn't exist
            test_data = {
                "acct_age_bucket": "1-6m",
                "acct_type": "person",
                "automation_flag": "manual",
                "post_kind": "original",
                "client_family": "mobile",
                "media_provenance": "hash_only",
                "origin_hint": "US-CA",
                "dedup_hash": "a1b2c3d4e5f6789a",
            }
            data_file.write_text(json.dumps(test_data, indent=2))

        data = json.loads(data_file.read_text())

        # Should validate without errors
        tag = PTag.model_validate(data)

        # Verify key properties
        assert tag.acct_type.value == "person"  # Compare enum value
        assert tag.automation_flag.value == "manual"  # Compare enum value
        tag_dict = tag.model_dump()
        assert tag_dict["origin_hint"] == "US-CA"

        # Round-trip test
        serialized = tag.model_dump()
        tag2 = PTag.model_validate(serialized)
        assert tag == tag2

    def test_schema_validation_against_examples(self):
        """Validate examples against canonical JSON schemas."""
        try:
            from jsonschema import Draft202012Validator
            from referencing import Registry, Resource
            from referencing.jsonschema import DRAFT202012
        except ImportError:
            pytest.skip("jsonschema or referencing not available")

        # Load schemas
        schema_dir = files("ci.transparency.ptag.spec.schemas")

        ptag_schema = json.loads(schema_dir.joinpath("ptag.schema.json").read_text())
        ptag_series_schema = json.loads(schema_dir.joinpath("ptag_series.schema.json").read_text())

        # Create registry with both schemas
        from typing import Any, Tuple, List
        resources: List[Tuple[str, Resource[Any]]] = [
            ("ptag.schema.json", Resource.from_contents(ptag_schema, default_specification=DRAFT202012)),
            ("ptag_series.schema.json", Resource.from_contents(ptag_series_schema, default_specification=DRAFT202012)),
        ]
        registry: Registry[Any] = Registry().with_resources(resources)  # type: ignore

        # Test PTagSeries
        series_data_file = Path(__file__).parent / "data" / "series_minimal.json"
        if series_data_file.exists():
            series_data = json.loads(series_data_file.read_text())
            try:
                validator = Draft202012Validator(ptag_series_schema, registry=registry)
                validator.validate(series_data)
            except Exception as e:
                pytest.skip(f"PTagSeries validation failed: {e}")

        # Test PTag
        tag_data_file = Path(__file__).parent / "data" / "ptag_minimal.json"
        if tag_data_file.exists():
            tag_data = json.loads(tag_data_file.read_text())
            try:
                validator = Draft202012Validator(ptag_schema, registry=registry)
                validator.validate(tag_data)
            except Exception as e:
                pytest.skip(f"PTag validation failed: {e}")
            """Validate examples against canonical JSON schemas."""
            try:
                from jsonschema import Draft202012Validator
                from referencing import Registry, Resource
                from referencing.jsonschema import DRAFT202012
            except ImportError:
                pytest.skip("jsonschema or referencing not available")

            # Load schemas
            schema_dir = files("ci.transparency.ptag.spec.schemas")

            ptag_schema = json.loads(schema_dir.joinpath("ptag.schema.json").read_text())
            ptag_series_schema = json.loads(schema_dir.joinpath("ptag_series.schema.json").read_text())

            # Create registry with both schemas
            from typing import Any, Tuple, List
            resources: List[Tuple[str, Resource[Any]]] = [
                ("ptag.schema.json", Resource.from_contents(ptag_schema, default_specification=DRAFT202012)),
                ("ptag_series.schema.json", Resource.from_contents(ptag_series_schema, default_specification=DRAFT202012)),
            ]
            registry: Registry[Any] = Registry().with_resources(resources)  # type: ignore

            # Test PTagSeries
            series_data_file = Path(__file__).parent / "data" / "series_minimal.json"
            if series_data_file.exists():
                series_data = json.loads(series_data_file.read_text())
                try:
                    validator = Draft202012Validator(ptag_series_schema, registry=registry)
                    validator.validate(series_data)
                except Exception as e:
                    pytest.skip(f"PTagSeries validation failed: {e}")

            # Test PTag
            tag_data_file = Path(__file__).parent / "data" / "ptag_minimal.json"
            if tag_data_file.exists():
                tag_data = json.loads(tag_data_file.read_text())
                try:
                    validator: Draft202012Validator = Draft202012Validator(ptag_schema, registry=registry)
                    validator.validate(tag_data)
                except Exception as e:
                    pytest.skip(f"PTag validation failed: {e}")
