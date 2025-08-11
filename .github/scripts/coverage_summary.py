# .github/scripts/coverage_summary.py
import xml.etree.ElementTree as ET
import os
from pathlib import Path

cov = Path("coverage.xml")
if not cov.exists():
    print("coverage.xml not found; nothing to summarize.")
    raise SystemExit(0)

tree = ET.parse(cov)
root = tree.getroot()

lines_valid = int(root.get("lines-valid", 0) or 0)
lines_covered = int(root.get("lines-covered", 0) or 0)
branches_valid = int(root.get("branches-valid", 0) or 0)
branches_covered = int(root.get("branches-covered", 0) or 0)

pct = (100.0 * lines_covered / lines_valid) if lines_valid else 0.0
bpct = (100.0 * branches_covered / branches_valid) if branches_valid else 0.0

summary = f"""## Coverage Summary
- Lines: **{lines_covered}/{lines_valid}** ({pct:.1f}%)
- Branches: **{branches_covered}/{branches_valid}** ({bpct:.1f}%)
"""

out = os.environ.get("GITHUB_STEP_SUMMARY")
if out:
    with open(out, "a", encoding="utf-8") as f:
        f.write(summary)
else:
    print(summary)
