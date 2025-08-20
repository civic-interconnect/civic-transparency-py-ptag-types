# scripts/generate_types.py
import subprocess
import sys
import hashlib
from pathlib import Path
from importlib.resources import as_file, files
from importlib.metadata import version as pkgver

SCHEMA_PKG = "ci.transparency.spec.schemas"
OUT_DIR = Path("src/ci/transparency/types")


def _add_schema_header(file_path, schema_name):
    """Add provenance header that pre-commit hooks expect."""
    # Normalize line endings BEFORE calculating hash
    _normalize_line_endings(file_path)

    schema_file = files(SCHEMA_PKG) / schema_name
    schema_text = schema_file.read_text()
    schema_sha = hashlib.sha256(schema_text.encode("utf-8")).hexdigest()
    spec_ver = pkgver("civic-transparency-spec")

    content = file_path.read_text()
    header = (
        "# AUTO-GENERATED: do not edit by hand\n"
        f"# source-schema: {schema_name}\n"
        f"# schema-sha256: {schema_sha}\n"
        f"# spec-version: {spec_ver}\n"
    )
    file_path.write_text(header + content)
    _normalize_line_endings(file_path)
    print(f"Added schema header to {file_path.name}")


def _fix_points_field(series_file):
    """Replace the multi-line points Field with default_factory=list."""
    content: str = series_file.read_text()
    lines: list[str] = content.splitlines()

    # Find the start of the points field
    points_start = None
    for i, line in enumerate(lines):
        if "points: List[Point] = Field(" in line:
            points_start = i
            break

    if points_start is None:
        print("ERROR: Points field not found")
        return False

    # Find the end of the Field definition
    paren_count = 0
    points_end = points_start
    for i in range(points_start, len(lines)):
        line = lines[i]
        paren_count += line.count("(") - line.count(")")
        if paren_count == 0 and i > points_start:
            points_end = i
            break

    print(f"Replacing points field (lines {points_start + 1}-{points_end + 1})")

    # Get indentation from original line
    original_line = lines[points_start]
    indent = len(original_line) - len(original_line.lstrip())
    indentation = " " * indent

    # Replace with simple default_factory version
    new_line = f"{indentation}points: List[Point] = Field(default_factory=list)"

    # Build new content
    new_lines = lines[:points_start] + [new_line] + lines[points_end + 1 :]

    series_file.write_text("\n".join(new_lines))
    print("Fixed points field")
    return True


def _normalize_line_endings(file_path):
    """Convert CRLF to LF to match what ruff expects."""
    content = file_path.read_bytes()
    if b"\r\n" in content:
        content = content.replace(b"\r\n", b"\n")
        file_path.write_bytes(content)
        print(f"Normalized line endings in {file_path.name}")


def _rename_seriesdoc_to_series(series_file):
    """Rename SeriesDoc class to Series for cleaner Python API."""
    content = series_file.read_text()
    content = content.replace("class SeriesDoc(", "class Series(")
    series_file.write_text(content)
    print("Renamed SeriesDoc to Series")


def main():
    print("Generating types...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate each file
    for schema_file, py_file in [
        ("series.schema.json", "series.py"),
        ("provenance_tag.schema.json", "provenance_tag.py"),
    ]:
        print(f"Generating {py_file}...")
        with as_file(files(SCHEMA_PKG) / schema_file) as schema_path:
            cmd = [
                sys.executable,
                "-m",
                "datamodel_code_generator",
                "--input",
                str(schema_path),
                "--input-file-type",
                "jsonschema",
                "--output",
                str(OUT_DIR / py_file),
                "--output-model-type",
                "pydantic_v2.BaseModel",
                "--target-python-version",
                "3.11",
                "--disable-timestamp",
            ]
            subprocess.run(cmd, check=True)

        # Post-process Python files
        file_path = OUT_DIR / py_file
        if py_file == "series.py":
            _fix_points_field(file_path)
            _rename_seriesdoc_to_series(file_path)

        _add_schema_header(file_path, schema_file)

    series_file = OUT_DIR / "series.py"
    series_content = series_file.read_text()

    # Check what classes exist
    available_classes = []
    imports = []

    if "class Series(" in series_content:
        available_classes.append("Series")
        imports.append("from .series import Series")

    if "class Interval(" in series_content:
        available_classes.append("Interval")
        imports.append("from .series import Interval")

    provenance_file = OUT_DIR / "provenance_tag.py"
    if provenance_file.exists():
        provenance_content = provenance_file.read_text()
        if "class ProvenanceTag(" in provenance_content:
            available_classes.append("ProvenanceTag")
            imports.append("from .provenance_tag import ProvenanceTag")

    # Write __init__.py with actual available classes
    init_content = "\n".join(imports) + "\n"
    init_content += "from ._version import __version__  # noqa: F401\n"
    init_content += f"__all__ = {available_classes!r}\n"
    (OUT_DIR / "__init__.py").write_text(init_content)
    print(f"Updated __init__.py to export: {available_classes}")

    print("Generation complete.")


if __name__ == "__main__":
    main()
