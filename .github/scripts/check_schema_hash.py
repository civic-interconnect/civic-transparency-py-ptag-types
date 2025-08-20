#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import re
from pathlib import Path
from importlib.resources import files

SRC = Path("src/ci/transparency/types")
TARGETS = {
    "series.schema.json": SRC / "series.py",
    "provenance_tag.schema.json": SRC / "provenance_tag.py",
}


def _header_val(text: str, key: str) -> str | None:
    m = re.search(rf"^#\s*{re.escape(key)}:\s*([0-9a-zA-Z._-]+)\s*$", text, re.M)
    return m.group(1) if m else None


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> int:
    # Load installed schemas from the spec package
    pkg = "ci.transparency.spec.schemas"
    ok = True
    for schema_name, py_path in TARGETS.items():
        if not py_path.exists():
            print(f"FAIL: missing generated file: {py_path}")
            ok = False
            continue
        head = py_path.read_text(encoding="utf-8").splitlines()[:20]
        header = "\n".join(head)

        stamped_name = _header_val(header, "source-schema")
        stamped_sha = _header_val(header, "schema-sha256")

        if stamped_name != schema_name or not stamped_sha:
            print(f"FAIL: {py_path} missing schema header or wrong schema name.")
            ok = False
            continue

        # compute actual hash from installed spec
        schema_text = (files(pkg) / schema_name).read_text(encoding="utf-8")
        actual_sha = _sha256(schema_text)

        if actual_sha != stamped_sha:
            print(f"FAIL: {py_path} schema hash mismatch.")
            print(f"  stamped: {stamped_sha}")
            print(f"  actual : {actual_sha}")
            print(
                "  Run: python scripts/generate_types.py && git add src/ci/transparency/types/"
            )
            ok = False

    # Bonus: assert points can be empty using the committed models
    try:
        from ci.transparency.types import Series  # uses committed source

        Series.model_validate(
            {
                "topic": "#hashcheck",
                "generated_at": "2025-01-01T00:00:00Z",
                "interval": "minute",
                "points": [],
            }
        )
    except Exception as e:
        print(f"FAIL: Series empty points validation failed: {e}")
        ok = False

    print(
        "PASS: schema hashes & empty-points invariant OK"
        if ok
        else "See failures above."
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
