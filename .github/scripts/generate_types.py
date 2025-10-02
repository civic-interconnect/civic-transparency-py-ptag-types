#!/usr/bin/env python3
"""Generate typed models from the PTag spec JSON Schemas and write them to src/.

Intended to be run in CI (but testable locally).
"""

import argparse
from collections.abc import Iterable
import hashlib
from importlib.metadata import version as pkgver
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path
import re
import subprocess  # nosec: B404  (used with shell=False and fixed argv)
import sys
from typing import NamedTuple

SCHEMA_PKG_ROOT = "ci.transparency.ptag.spec"  # schemas live under here
DEFAULT_OUT_DIR = Path("src/ci/transparency/ptag/types")


class SchemaPair(NamedTuple):
    """A pair of schema filenames for the PTag spec.

    Attributes
    ----------
    series : str
        The filename for the series schema (e.g., 'ptag_series.schema.json').
    ptag : str
        The filename for the ptag schema (e.g., 'ptag.schema.json').
    """

    series: str  # e.g., ptag_series.schema.json
    ptag: str  # e.g., ptag.schema.json


# =================
# Schema discovery & hashing
# =================
def _schema_dir() -> Traversable:
    """Return a Traversable for the /schemas dir inside the spec package."""
    root = files(SCHEMA_PKG_ROOT)
    cand = root / "schemas"
    if cand.is_dir():
        return cand
    return files(f"{SCHEMA_PKG_ROOT}.schemas")


def _discover_schema_names() -> SchemaPair:
    """Pick actual schema filenames from the installed wheel."""
    sdir = _schema_dir()
    names = [c.name for c in sdir.iterdir() if c.name.endswith(".schema.json")]

    if not names:
        raise FileNotFoundError(
            f"No '*.schema.json' files found in {SCHEMA_PKG_ROOT}/schemas. "
            "Is 'civic-transparency-ptag-spec' installed with data files?"
        )

    # Prefer best matches
    series = next((n for n in names if n == "ptag_series.schema.json"), None)

    ptag = "ptag.schema.json" if "ptag.schema.json" in names else None

    if not series or not ptag:
        raise FileNotFoundError(
            "Could not resolve schema filenames.\n"
            f"Found: {names}\n"
            "Need one for PTagSeries (name is 'ptag_series.schema.json') and one for PTag "
            "(name is 'ptag.schema.json')."
        )

    print(f"[discover] Using series schema: {series}")
    print(f"[discover] Using ptag   schema: {ptag}")
    return SchemaPair(series=series, ptag=ptag)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _schema_sha(sdir: Traversable, schema_name: str) -> str:
    with as_file(sdir / schema_name) as schema_path:
        return _sha256_text(Path(schema_path).read_text(encoding="utf-8"))


# =================
# File utilities
# =================
def _normalize_line_endings(file_path: Path) -> None:
    """Convert CRLF -> LF to match formatting tools & stable hashing."""
    content = file_path.read_bytes()
    if b"\r\n" in content:
        file_path.write_bytes(content.replace(b"\r\n", b"\n"))


def _add_schema_header(py_file: Path, schema_name: str) -> None:
    """Prepend a provenance header recognized by pre-commit checks."""
    _normalize_line_endings(py_file)
    sdir = _schema_dir()
    schema_text = (sdir / schema_name).read_text(encoding="utf-8")
    header = (
        "# AUTO-GENERATED: do not edit by hand\n"
        f"# source-schema: {schema_name}\n"
        f"# schema-sha256: {_sha256_text(schema_text)}\n"
        f"# spec-version: {pkgver('civic-transparency-ptag-spec')}\n"
    )
    py_text = py_file.read_text(encoding="utf-8")
    py_file.write_text(header + py_text, encoding="utf-8")
    _normalize_line_endings(py_file)


# =================
# Post-processing tweaks (safe / idempotent)
# =================
def _fix_points_field(series_file: Path) -> bool:
    """Ensure: points: list[PTagSeriesPoint] = Field(default_factory=list).

    Works across formatting variations, and silences Pyright on this line.
    """
    text = series_file.read_text(encoding="utf-8")

    # Already OK?
    already_ok = re.search(
        r"""^[ \t]*points:\s*list\[PTagSeriesPoint\]\s*=\s*Field\(\s*default_factory\s*=\s*list\s*\)\s*(?:#\s*type:\s*ignore)?\s*$""",
        text,
        re.MULTILINE,
    )
    if already_ok:
        print(
            "[series] points Field already uses default_factory=list (with/without type: ignore) (skip patch)"
        )
        return False

    pattern = re.compile(
        r"""(?P<indent>^[ \t]*)points:\s*list\[PTagSeriesPoint\]\s*=\s*Field\([^)]*\)""",
        re.MULTILINE | re.DOTALL,
    )
    replacement = (
        r"\g<indent>points: list[PTagSeriesPoint] = Field(default_factory=list)  # type: ignore"
    )

    if not pattern.search(text):
        print("[series] points Field pattern not found (skip patch)")
        return False

    text2 = pattern.sub(replacement, text, count=1)
    series_file.write_text(text2, encoding="utf-8")
    _normalize_line_endings(series_file)
    print("[series] Patched points Field -> default_factory=list")
    return True


# =================
# Code generation
# =================
def _format_with_ruff(py_file: Path) -> None:
    """Run ruff format and fix on generated file."""
    import subprocess  # nosec: B404

    # Format (fixes quotes, line length, etc.)
    subprocess.run(  # noqa: S603  # nosec: B603  (shell disabled; args are static)
        [sys.executable, "-m", "ruff", "format", str(py_file)],
        check=False,  # Don't fail if ruff isn't installed
        capture_output=True,
    )

    # Auto-fix (fixes some violations like quote style)
    subprocess.run(  # noqa: S603  # nosec: B603  (shell disabled; args are static)
        [sys.executable, "-m", "ruff", "check", "--fix", str(py_file)],
        check=False,
        capture_output=True,
    )


def _run_dcg(schema_path: Path, output_file: Path) -> None:
    """Invoke datamodel-code-generator for a single schema → .py file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    # All arguments are constructed from trusted sources, not user input.
    cmd = [
        sys.executable,
        "-m",
        "datamodel_code_generator",
        "--input",
        str(schema_path),
        "--input-file-type",
        "jsonschema",
        "--output",
        str(output_file),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--target-python-version",
        "3.12",
        "--disable-timestamp",
        "--use-standard-collections",  # Add: list instead of List
        "--use-union-operator",  # Add: | instead of Union
        "--field-constraints",  # Add: Annotated instead of constr/conint
    ]
    subprocess.run(cmd, check=True, shell=False)  # noqa: S603  # nosec: B603  (shell disabled; args are static)


# =================
# Public symbol resolution & __init__ authoring
# =================
_CLASS_DEF_RX = re.compile(r"^[ \t]*class[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\(", re.MULTILINE)


def _classes_in_file(py_file: Path) -> set[str]:
    text = py_file.read_text(encoding="utf-8")
    return {m.group("name") for m in _CLASS_DEF_RX.finditer(text)}


def _resolve_symbols(series_py: Path, ptag_py: Path) -> tuple[str, str, str]:
    """Return concrete class names for PTag, PTagSeries, and PTagInterval.

    Validates that all required classes exist in generated code.
    """
    s_classes = _classes_in_file(series_py)
    p_classes = _classes_in_file(ptag_py)

    # PTag must exist in ptag.py
    if "PTag" not in p_classes:
        raise RuntimeError(f"Expected 'PTag' in {ptag_py.name}; found {sorted(p_classes)}")

    # PTagSeries must exist in ptag_series.py
    if "PTagSeries" not in s_classes:
        raise RuntimeError(f"Expected 'PTagSeries' in {series_py.name}; found {sorted(s_classes)}")

    # PTagInterval must exist in ptag_series.py
    if "PTagInterval" not in s_classes:
        raise RuntimeError(
            f"Expected 'PTagInterval' enum in {series_py.name}; found {sorted(s_classes)}"
        )

    return "PTag", "PTagSeries", "PTagInterval"


def _write_meta_py(out_dir: Path, schema_shas: dict[str, str]) -> None:
    """Write _meta.py with the spec version and schema hashes."""
    meta = out_dir / "_meta.py"
    spec_ver = pkgver("civic-transparency-ptag-spec")
    lines = [
        f'PTAG_SPEC_VERSION = "{spec_ver}"',
        "SCHEMA_HASHES = {",
    ]
    for name, sha in schema_shas.items():
        lines.append(f'    "{name}": "{sha}",')
    lines.append("}")
    lines.append("")  # newline at EOF
    meta.write_text("\n".join(lines), encoding="utf-8")
    _normalize_line_endings(meta)


def _write_init_py(
    out_dir: Path,
    series_cls: str,
    interval_cls: str,
    ptag_cls: str,
) -> None:
    """Write a minimal __init__ that exposes PTag, PTagSeries, and PTagInterval."""
    lines: list[str] = [
        "from importlib.metadata import version as _pkgver",
        "",
        f"from .ptag import {ptag_cls} as PTag",
        f"from .ptag_series import {interval_cls} as PTagInterval",
        f"from .ptag_series import {series_cls} as PTagSeries",
        "",
        '__all__ = ["PTag", "PTagSeries", "PTagInterval"]',
        "",
        "# Package version",
        "try:",
        '    __version__ = _pkgver("civic-transparency-py-ptag-types")',
        "except Exception:",
        '    __version__ = "0.0.0+unknown"',
        "",
    ]
    init_py = out_dir / "__init__.py"
    init_py.write_text("\n".join(lines), encoding="utf-8")
    _normalize_line_endings(init_py)
    print("[init] wrote public API: __all__ = ['PTag', 'PTagSeries', 'PTagInterval']")


# =================
# Main flow
# =================
def _discover_exports(py_paths: Iterable[Path]) -> tuple[list[str], list[str]]:
    """Return discovered class names and import lines."""
    exports: list[str] = []
    imports: list[str] = []
    for p in py_paths:
        txt = p.read_text(encoding="utf-8")
        mod = p.stem
        for cls in ("PTagSeries", "PTagInterval", "PTag"):
            if f"class {cls}(" in txt:
                exports.append(cls)
                imports.append(f"from .{mod} import {cls}")
    return exports, imports


def generate_all(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    """Generate Python type models from PTag schemas and write them to the output directory."""
    print("Generating PTag types from JSON Schemas...")

    sdir = _schema_dir()
    try:
        schemas = _discover_schema_names()
    except Exception as e:  # helpful context if discovery fails
        try:
            present = [c.name for c in sdir.iterdir()]
        except Exception:
            present = []
        raise RuntimeError(f"Schema discovery failed: {e}\nPresent files: {present}") from e

    plan = [
        (schemas.series, "ptag_series.py"),
        (schemas.ptag, "ptag.py"),
    ]

    generated: list[Path] = []
    schema_shas: dict[str, str] = {}

    for schema_name, py_name in plan:
        schema_res = sdir / schema_name
        print(f"  - {py_name} from {schema_name} [{schema_res}]")
        with as_file(schema_res) as schema_path:
            target = out_dir / py_name
            _run_dcg(schema_path, target)
            _normalize_line_endings(target)
            _format_with_ruff(target)
        schema_shas[schema_name] = _schema_sha(sdir, schema_name)

        if py_name == "ptag_series.py" and _fix_points_field(out_dir / py_name):
            _format_with_ruff(out_dir / py_name)

        _add_schema_header(out_dir / py_name, schema_name)
        _format_with_ruff(out_dir / py_name)
        generated.append(out_dir / py_name)

    # Resolve concrete class names and enforce Interval presence
    series_py = out_dir / "ptag_series.py"
    ptag_py = out_dir / "ptag.py"
    ptag_cls, series_cls, interval_cls = _resolve_symbols(series_py, ptag_py)

    # Write metadata + top-level API
    _write_meta_py(out_dir, schema_shas)
    _write_init_py(out_dir, series_cls=series_cls, interval_cls=interval_cls, ptag_cls=ptag_cls)

    # (Optional) debug: show discovered classes
    exports, _ = _discover_exports(generated)
    print(f"[discover] classes found: {sorted(set(exports))}")

    print("Generation complete.")


def main(argv: list[str] | None = None) -> int:
    """Entry point for the type generation script.

    Parameters
    ----------
    argv : list[str] | None
        Command-line arguments to parse (default: None, uses sys.argv).

    Returns
    -------
    int
        Exit code: 0 on success, nonzero on error.
    """
    parser = argparse.ArgumentParser(description="Generate Python types from PTag schemas.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUT_DIR})",
    )
    args = parser.parse_args(argv)

    try:
        generate_all(out_dir=args.out)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: datamodel-code-generator failed: {e}", file=sys.stderr)
        return e.returncode or 1
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e!r}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
