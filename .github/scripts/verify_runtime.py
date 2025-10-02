"""Script to verify runtime compatibility of PTag and PTagSeries models.

This script instantiates and serializes PTag and PTagSeries objects to ensure they work as expected.
"""

#!/usr/bin/env python3
from datetime import UTC, datetime
from pathlib import Path
import sys

from ci.transparency.ptag.types import PTag, PTagSeries

# dev-only import helper; safe in CI and local editors
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    """Verify that PTag and PTagSeries models can be instantiated and serialized without errors."""
    # Use model_validate instead of direct instantiation - bypasses type checking
    tag = PTag.model_validate(
        {
            "acct_age_bucket": "1-6m",
            "acct_type": "person",
            "automation_flag": "manual",
            "post_kind": "original",
            "client_family": "mobile",
            "media_provenance": "hash_only",
            "dedup_hash": "a1b2c3d4",
            "origin_hint": "US-CA",  # Optional - can omit entirely
            # "content_digest": "abc123def456",  # Optional - can omit entirely
        }
    )

    series = PTagSeries.model_validate(
        {
            "topic": "#CompatibilityTest",
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "interval": "5-minute",  # String works fine
            "points": [],
        }
    )

    # JSON serialization
    _ = tag.model_dump_json()
    _ = series.model_dump_json()

    print("SUCCESS: Runtime compatibility verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
