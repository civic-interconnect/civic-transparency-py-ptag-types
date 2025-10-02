#!/usr/bin/env python3
"""Deterministic release preflight for CT Types.

What it does:
  1) Normalize a provided tag (e.g. "v0.2.5" -> "0.2.5") and export
     SETUPTOOLS_SCM_PRETEND_VERSION=<plain>.
  2) Run "uv build" to create dist/*.
  3) Verify the wheel filename version == tag's plain version.
  4) (optional) Regenerate types to a temp dir and diff with committed files.
  5) (optional) Run tests: "uv run -m pytest -q".
  6) List artifacts and exit(0) if all checks pass.

Usage (local):
  uv run python .github/scripts/release_check.py --tag v0.2.5 --ensure-types --run-tests

Usage (CI):
  - name: Release preflight
    run: uv run python .github/scripts/release_check.py --tag "$GITHUB_REF_NAME" --ensure-types --run-tests
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess  # nosec B404 - controlled use; see run_cmd; shell=False everywhere
import sys
import tempfile

# No need to import Iterable or Tuple; use built-in tuple instead

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_DIR = REPO_ROOT / "dist"
TYPES_DIR = REPO_ROOT / "src" / "ci" / "transparency" / "ptag" / "types"
GEN_SCRIPT = REPO_ROOT / ".github" / "scripts" / "generate_types.py"

WHEEL_NAME_RX = re.compile(r"civic[_-]transparency[_-]types-([0-9][^-]*)-py", re.IGNORECASE)


def _run(cmd: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    """Run a subprocess with shell disabled and fail fast."""
    print(f"+ {' '.join(cmd)}")
    cp = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, shell=False)  # noqa: S603 # nosec B603 - args are static/validated; shell=False; no untrusted input
    if cp.returncode != 0:
        raise SystemExit(cp.returncode)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _list_artifacts() -> None:
    if not DIST_DIR.exists():
        print("dist/ missing")
        return
    print("\nArtifacts in dist/:")
    for p in sorted(DIST_DIR.glob("*")):
        sz = p.stat().st_size
        print(f"  - {p.name}  ({sz:,} bytes)")


def _wheel_version() -> str:
    wheels = sorted(DIST_DIR.glob("*.whl"))
    if not wheels:
        raise SystemExit("ERROR: no wheel found in dist/")
    w = wheels[0]
    m = WHEEL_NAME_RX.search(w.name)
    if not m:
        raise SystemExit(f"ERROR: cannot parse version from wheel name: {w.name}")
    return m.group(1)


def _normalize_tag(tag: str) -> tuple[str, str]:
    """Return (raw_tag, plain_version) where plain drops a leading 'v' if present."""
    raw = tag.strip()
    plain = raw[1:] if raw.startswith("v") else raw
    if not re.fullmatch(r"\d+\.\d+\.\d+[0-9A-Za-z\.\-\+]*", plain):
        raise SystemExit(f"ERROR: tag '{tag}' doesn't look like a version (got '{plain}')")
    return raw, plain


def _compare_dirs(a: Path, b: Path) -> list[str]:
    """Return a list of human-readable diffs; empty list means identical."""
    diffs: list[str] = []
    a_files = {p.relative_to(a): p for p in a.rglob("*") if p.is_file()}
    b_files = {p.relative_to(b): p for p in b.rglob("*") if p.is_file()}

    missing_in_b = sorted(set(a_files) - set(b_files))
    missing_in_a = sorted(set(b_files) - set(a_files))
    if missing_in_b:
        diffs.append(f"Missing in committed types: {', '.join(str(x) for x in missing_in_b)}")
    if missing_in_a:
        diffs.append(f"Extra files in committed types: {', '.join(str(x) for x in missing_in_a)}")

    for rel in sorted(set(a_files) & set(b_files)):
        if _sha256_file(a_files[rel]) != _sha256_file(b_files[rel]):
            diffs.append(f"Content differs: {rel}")
    return diffs


def ensure_types_no_drift() -> None:
    """Regenerate to a temp dir and diff vs committed TYPES_DIR."""
    if not GEN_SCRIPT.exists():
        raise SystemExit(f"ERROR: generator not found: {GEN_SCRIPT}")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        print(f"Regenerating types into: {out}")
        _run([sys.executable, str(GEN_SCRIPT), "--out", str(out)])
        print("Comparing regenerated vs committed…")
        diffs = _compare_dirs(out, TYPES_DIR)
        if diffs:
            print(
                "\nERROR: generated types differ from committed files:\n  - " + "\n  - ".join(diffs)
            )
            print(
                "\nFix locally:\n  uv run python .github/scripts/generate_types.py\n  git add src/ci/transparency/ptag/types"
            )
            raise SystemExit(1)
        print("OK: generated types match committed files.")


def main(argv: list[str] | None = None) -> int:
    """Run release preflight checks for CT Types.

    Parameters
    ----------
    argv : list[str] | None
        Command-line arguments to parse (default: None, uses sys.argv).

    Returns
    -------
    int
        Exit code: 0 if all checks pass, nonzero otherwise.
    """
    ap = argparse.ArgumentParser(description="Release preflight for CT Types.")
    ap.add_argument("--tag", required=True, help="Git tag (e.g., v0.2.5 or 0.2.5)")
    ap.add_argument("--ensure-types", action="store_true", help="Regenerate & diff types")
    ap.add_argument("--run-tests", action="store_true", help="Run 'uv run -m pytest -q'")
    args = ap.parse_args(argv)

    raw_tag, plain = _normalize_tag(args.tag)
    print(f"Tag: {raw_tag}  → version: {plain}")

    # Clean dist/ for a deterministic build
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    # Build with pinned version from tag
    env = os.environ.copy()
    env["SETUPTOOLS_SCM_PRETEND_VERSION"] = plain
    _run(["uv", "build"], env=env, cwd=REPO_ROOT)

    # Version sanity check
    have = _wheel_version()
    if have != plain:
        print(f"ERROR: wheel version ({have}) != tag version ({plain})")
        return 1
    print(f"OK: wheel version matches tag ({have})")

    # Optional: types drift check
    if args.ensure_types:
        ensure_types_no_drift()

    # Optional: tests
    if args.run_tests:
        _run(["uv", "run", "-m", "pytest", "-q"], cwd=REPO_ROOT)

    # Show artifacts
    _list_artifacts()
    print("\nAll preflight checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
