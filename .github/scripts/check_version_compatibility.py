#!/usr/bin/env python3
"""
Version/spec compatibility check for civic-transparency-types.

- Verifies the installed civic-transparency-spec satisfies pyproject's requirement
- Asserts series.schema.json allows empty points (minItems == 0)
- Asserts generated Series.points uses default_factory=list
- Prints import origins to catch shadowed installs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.version import Version

# Prefer installed packages; fall back to repo src for dev
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"

try:
    from importlib.metadata import PackageNotFoundError, version
except Exception:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

try:
    import tomllib  # py311+
except Exception:  # pragma: no cover
    import tomli as tomllib  # type: ignore


def _load_pyproject() -> dict:
    p = REPO_ROOT / "pyproject.toml"
    with p.open("rb") as f:
        return tomllib.load(f)


def _find_spec_requirement(pyproj: dict) -> Requirement | None:
    # Search [project].dependencies first
    for dep in pyproj.get("project", {}).get("dependencies", []):
        try:
            req = Requirement(dep)
        except Exception:
            continue
        if req.name == "civic-transparency-spec":
            return req
    # Also allow a pinned dev override in optional deps
    for dep in (
        pyproj.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    ):
        try:
            req = Requirement(dep)
        except Exception:
            continue
        if req.name == "civic-transparency-spec":
            return req
    return None


def _get_installed(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _assert_schema_invariant() -> None:
    # Load series.schema.json from the installed spec package
    from importlib.resources import files

    try:
        text = (
            files("ci.transparency.spec.schemas") / "series.schema.json"
        ).read_text()
    except Exception as e:
        raise SystemExit(
            f"FAIL: could not load series.schema.json from spec package: {e}"
        )

    try:
        schema = json.loads(text)
        min_items = schema["properties"]["points"].get("minItems", 0)
    except Exception as e:
        raise SystemExit(f"FAIL: series.schema.json malformed: {e}")

    if min_items != 0:
        raise SystemExit(
            f"FAIL: Spec invariant violated: points.minItems={min_items!r} (expected 0 or absent). "
            "Update civic-transparency-spec to a version that permits empty points."
        )

    print("Spec invariant OK: points.minItems == 0")


def _assert_types_points_default_factory() -> None:
    # Try import installed first; then fall back to src for dev mode
    try:
        import ci.transparency.types as types  # type: ignore
    except ImportError:
        sys.path.insert(0, str(SRC_PATH))
        import ci.transparency.types as types  # type: ignore

    print(f"types imported from: {getattr(types, '__file__', 'unknown')}")
    fld = types.Series.model_fields["points"]
    if fld.default_factory is None:
        raise SystemExit(
            "FAIL: Series.points has no default_factory=list. "
            "Regenerate models to allow empty arrays."
        )
    print("Types invariant OK: Series.points uses default_factory=list")


def main() -> int:
    print("Checking civic-transparency types/spec compatibility…")

    pyproj = _load_pyproject()
    req = _find_spec_requirement(pyproj)
    if not req:
        print("WARN: No civic-transparency-spec requirement found in pyproject.toml")
    else:
        print(f"Declared spec requirement: {req}")

    spec_ver = _get_installed("civic-transparency-spec")
    if not spec_ver:
        print(
            "FAIL: civic-transparency-spec is not installed. "
            "Install dev deps: pip install -e '.[dev]'"
        )
        return 1
    print(f"Installed spec version: {spec_ver}")

    # If a requirement is declared, ensure the installed version satisfies it.
    if req:
        if not req.specifier.contains(Version(spec_ver), prereleases=True):
            print(
                f"FAIL: Installed spec {spec_ver} does not satisfy requirement '{req.specifier}'"
            )
            return 1

    # Schema invariant (empty points allowed)
    _assert_schema_invariant()

    # Types invariant (generated model accepts empty points)
    _assert_types_points_default_factory()

    print("PASS: versions and invariants look good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
