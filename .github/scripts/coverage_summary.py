"""Script to parse coverage.xml and output a formatted coverage summary for GitHub Actions."""

# .github/scripts/coverage_summary.py
import os
from pathlib import Path

# defusedxml is a safer alternative to xml.etree.ElementTree
import defusedxml.ElementTree as ET  # noqa: N817 - ET is the common alias


def get_coverage_summary() -> str | None:
    """Parse a coverage.xml file and return a formatted summary."""
    cov = Path("coverage.xml")
    if not cov.exists():
        print("coverage.xml not found; nothing to summarize.")
        return None

    try:
        tree = ET.parse(cov)
        root = tree.getroot()
        if root is None:
            print("coverage.xml is missing a root element.")
            return None

        lines_valid_str = root.get("lines-valid", "0")
        lines_covered_str = root.get("lines-covered", "0")
        branches_valid_str = root.get("branches-valid", "0")
        branches_covered_str = root.get("branches-covered", "0")

        lines_valid = int(lines_valid_str) if lines_valid_str else 0
        lines_covered = int(lines_covered_str) if lines_covered_str else 0
        branches_valid = int(branches_valid_str) if branches_valid_str else 0
        branches_covered = int(branches_covered_str) if branches_covered_str else 0

        pct = (100.0 * lines_covered / lines_valid) if lines_valid else 0.0
        bpct = (100.0 * branches_covered / branches_valid) if branches_valid else 0.0

        return f"""### Coverage Summary
- Lines: **{lines_covered}/{lines_valid}** ({pct:.1f}%)
- Branches: **{branches_covered}/{branches_valid}** ({bpct:.1f}%)
"""
    except (ET.ParseError, ValueError) as e:
        print(f"Error parsing coverage.xml: {e}")
        return None


def main() -> None:
    """Run the script."""
    summary = get_coverage_summary()

    if summary:
        out = os.environ.get("GITHUB_STEP_SUMMARY")
        if out:
            out_path = Path(out)
            with out_path.open("a", encoding="utf-8") as f:
                f.write(summary)
        else:
            print(summary)


if __name__ == "__main__":
    main()
