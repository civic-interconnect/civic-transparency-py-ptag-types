"""Script to verify PTag and PTagSeries type validation and JSON serialization.

This script tests the instantiation and validation of PTag and PTagSeries objects,
as well as their JSON serialization, to ensure compatibility.
"""

from datetime import UTC, datetime

from ci.transparency.ptag.types import PTag, PTagSeries

# Test PTag validation (fixed hash length)
tag = PTag(
    acct_age_bucket="1-6m",
    acct_type="person",
    automation_flag="manual",
    post_kind="original",
    client_family="mobile",
    media_provenance="hash_only",
    dedup_hash="a1b2c3d4",
)
print("PTag validation works")

# Test PTagSeries validation
series = PTagSeries(
    topic="#CompatibilityTest",
    generated_at=datetime.now(UTC).replace(microsecond=0),
    interval="minute",
    points=[],
)
print("PTagSeries validation works")

# Test JSON serialization
tag_json = tag.model_dump_json()
series_json = series.model_dump_json()
print("JSON serialization works")

print("Compatibility verified: Python ${{ matrix.python-version }}")
