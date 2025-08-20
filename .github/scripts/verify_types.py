from ci.transparency.types import Series, ProvenanceTag
from datetime import datetime, timezone


# Test ProvenanceTag validation (fixed hash length)
tag = ProvenanceTag(
    acct_age_bucket="1-6m",
    acct_type="person",
    automation_flag="manual",
    post_kind="original",
    client_family="mobile",
    media_provenance="hash_only",
    dedup_hash="a1b2c3d4",
)
print("ProvenanceTag validation works")

# Test Series validation
series = Series(
    topic="#CompatibilityTest",
    generated_at=datetime.now(timezone.utc).replace(microsecond=0),
    interval="minute",
    points=[],
)
print("Series validation works")

# Test JSON serialization
tag_json = tag.model_dump_json()
series_json = series.model_dump_json()
print("JSON serialization works")

print("Compatibility verified: Python ${{ matrix.python-version }}")
