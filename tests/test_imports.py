# tests/test_imports.py
from ci.transparency.types import Meta, Run, Scenario, Series, ProvenanceTag


def test_imports():  # just proves modules exist
    assert Meta and Run and Scenario and Series and ProvenanceTag
