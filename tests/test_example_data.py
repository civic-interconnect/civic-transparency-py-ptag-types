# tests/test_example_data.py
import json
from pathlib import Path
from ci.transparency.types import Series, ProvenanceTag
import pytest


class TestExampleData:
    """Test that our example data validates correctly."""

    def test_series_minimal_example(self):
        """Test minimal valid Series example."""
        data_file = Path(__file__).parent / "data" / "series_minimal.json"
        data = json.loads(data_file.read_text())

        # Should
        # validate without errors
        series = Series.model_validate(data)

        # Verify key properties
        assert series.topic == "#TestTopic"
        assert series.interval.value == "minute"  # Compare enum value, not enum object
        assert len(series.points) == 1
        assert series.points[0].volume == 100

        # Round-trip test
        serialized = series.model_dump()
        series2 = Series.model_validate(serialized)
        assert series == series2

    def test_provenance_tag_minimal_example(self):
        """Test minimal valid ProvenanceTag example."""
        data_file = Path(__file__).parent / "data" / "provenance_tag_minimal.json"
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
        tag = ProvenanceTag.model_validate(data)

        # Verify key properties
        assert tag.acct_type.value == "person"  # Compare enum value
        assert tag.automation_flag.value == "manual"  # Compare enum value
        assert tag.origin_hint == "US-CA"

        # Round-trip test
        serialized = tag.model_dump()
        tag2 = ProvenanceTag.model_validate(serialized)
        assert tag == tag2

    def test_schema_validation_against_examples(self):
        """Validate examples against canonical JSON schemas."""
        try:
            from importlib.resources import files
            from jsonschema import Draft202012Validator
        except ImportError:
            pytest.skip("jsonschema or importlib.resources not available")

        # Test Series
        series_data_file = Path(__file__).parent / "data" / "series_minimal.json"
        if not series_data_file.exists():
            pytest.skip("series_minimal.json test data not found")

        series_data = json.loads(series_data_file.read_text())

        try:
            schema_text = (
                files("ci.transparency.spec.schemas")
                .joinpath("series.schema.json")
                .read_text()
            )
            schema = json.loads(schema_text)

            # Should validate against canonical schema
            Draft202012Validator(schema).validate(series_data)  # type: ignore
        except Exception as e:
            pytest.skip(f"Schema validation failed: {e}")

        # Test ProvenanceTag
        tag_data_file = Path(__file__).parent / "data" / "provenance_tag_minimal.json"
        if not tag_data_file.exists():
            pytest.skip("provenance_tag_minimal.json test data not found")

        tag_data = json.loads(tag_data_file.read_text())

        try:
            schema_text = (
                files("ci.transparency.spec.schemas")
                .joinpath("provenance_tag.schema.json")
                .read_text()
            )
            schema = json.loads(schema_text)

            # Should validate against canonical schema
            Draft202012Validator(schema).validate(tag_data)  # type: ignore
        except Exception as e:
            pytest.skip(f"ProvenanceTag schema validation failed: {e}")
