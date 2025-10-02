# tests/conftest.py

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".github" / "scripts"
SRC = ROOT / "src"

for p in (SRC, SCRIPTS):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
