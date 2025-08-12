# .github/scripts/list_artifacts.py
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

DIST = Path("dist")


def main() -> int:
    if not DIST.exists():
        print("ERROR: dist/ does not exist")
        return 1

    files = sorted(DIST.glob("*"))
    if not files:
        print("ERROR: dist/ is empty")
        return 1

    print("Dist files:")
    for f in files:
        print(" -", f)

    wheels = sorted(DIST.glob("*.whl"))
    sdists = sorted(DIST.glob("*.tar.gz"))

    if not wheels:
        print("ERROR: No wheel (*.whl) found in dist/")
        return 1
    if not sdists:
        print("ERROR: No sdist (*.tar.gz) found in dist/")
        return 1

    # Inspect wheels for schema & OpenAPI files (informational; not failing)
    for whl in wheels:
        with zipfile.ZipFile(whl) as z:
            names = z.namelist()
            schemas = [n for n in names if n.endswith(".schema.json")]
            openapis = [n for n in names if n.endswith(".openapi.yaml")]
            print(f"\n{whl.name}")
            print("   JSON Schemas:")
            for s in schemas or ["(none found)"]:
                print("    •", s)
            print("   OpenAPI files:")
            for o in openapis or ["(none found)"]:
                print("    •", o)

    return 0


if __name__ == "__main__":
    sys.exit(main())
