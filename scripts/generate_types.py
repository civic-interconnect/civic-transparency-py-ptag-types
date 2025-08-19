# scripts/generate_types.py
from __future__ import annotations

import subprocess
import sys
from importlib.resources import files, as_file
from pathlib import Path

# Schemas come from the installed *spec* package
SCHEMA_PKG = "ci.transparency.spec.schemas"

# Output package for generated models (this repo)
OUT_DIR = Path("src/ci/transparency/types")

# Map input schema filename -> output module + root class name
TARGETS = {
    "series.schema.json": ("series.py", "Series"),
    "provenance_tag.schema.json": ("provenance_tag.py", "ProvenanceTag"),
}


def _ensure_init_exports(init_path: Path) -> None:
    required_lines = [
        "from .series import Series",
        "from .provenance_tag import ProvenanceTag",
        "from ._version import __version__  # noqa: F401",
        "__all__ = ['Series', 'ProvenanceTag']",
    ]

    existing = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
    lines = [ln.rstrip() for ln in existing.splitlines() if ln.strip()]

    changed = False
    for req in required_lines:
        if not any(ln == req for ln in lines):
            lines.append(req)
            changed = True

    new_text = "\n".join(lines) + ("\n" if lines else "")
    if changed or existing != new_text:
        init_path.write_text(new_text, encoding="utf-8")
        print("Updated __init__.py exports")
    else:
        print("Keeping existing __init__.py (no changes)")


def _run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.check_call(cmd)


def _strip_unused_rootmodel(import_file: Path) -> None:
    """Remove `RootModel` from `from pydantic import ...` if not used elsewhere."""
    text = import_file.read_text(encoding="utf-8")
    # If it's not present, nothing to do
    if "RootModel" not in text:
        return
    # If the *only* occurrence is the import line, we can safely drop it
    lines = text.splitlines()
    joined_without_import = "\n".join(
        ln
        for ln in lines
        if not (ln.startswith("from pydantic import") and "RootModel" in ln)
    )
    if "RootModel" in joined_without_import:
        # It's used somewhere else; keep it.
        return

    # Rewrite the import line, removing RootModel token
    new_lines: list[str] = []
    for ln in lines:
        if ln.startswith("from pydantic import") and "RootModel" in ln:
            # split imports, drop the token, rejoin cleanly
            head, tail = ln.split("import", 1)
            parts = [p.strip() for p in tail.split(",")]
            parts = [p for p in parts if p != "RootModel"]
            # Only rewrite if anything remains
            if parts:
                ln = f"{head}import {', '.join(parts)}"
            else:
                # If nothing remains, drop the entire line
                ln = ""
        new_lines.append(ln)
    import_file.write_text(
        "\n".join([line for line in new_lines if line.strip()]), encoding="utf-8"
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ensure package init exists before writes
    (OUT_DIR / "__init__.py").touch(exist_ok=True)

    for schema_name, (out_py, root_class) in TARGETS.items():
        # Locate resource inside installed package
        res = files(SCHEMA_PKG).joinpath(schema_name)
        if not res.is_file():
            print(
                f"ERROR: schema not found in package {SCHEMA_PKG}: {schema_name}",
                file=sys.stderr,
            )
            return 1

        # Make sure we pass a real filesystem path to the generator
        with as_file(res) as schema_path:
            out_path = OUT_DIR / out_py
            cmd = [
                sys.executable,
                "-m",
                "datamodel_code_generator",
                "--input",
                str(schema_path),
                "--input-file-type",
                "jsonschema",
                "--output",
                str(out_path),
                "--output-model-type",
                "pydantic_v2.BaseModel",
                "--target-python-version",
                "3.11",
                "--class-name",
                root_class,
                "--disable-timestamp",  # reproducible output
                "--use-schema-description",  # carry descriptions to Field(..., description=)
                "--collapse-root-models",  # nicer one-class roots
                "--wrap-string-literal",  # readable long literals
                "--use-annotated",  # use Annotated for constraints
            ]
            _run(cmd)
            _strip_unused_rootmodel(out_path)

    # Export friendly names
    init_path = OUT_DIR / "__init__.py"
    _ensure_init_exports(init_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
