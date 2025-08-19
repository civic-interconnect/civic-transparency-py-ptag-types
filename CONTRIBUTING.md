# CONTRIBUTING.md

This repo hosts the **Civic Transparency Types** under the **MIT License**.
Our goals are clarity, privacy-by-design, and low friction for collaborators.

> tl;dr: open an Issue or Discussion first for anything non-trivial, keep PRs small and focused, and please run the quick local checks below.

---

## Ways to Contribute

- **Docs**: Fix typos, clarify definitions, or improve examples in `docs/en/**`.
- **Actions**: Propose changes to project workflow and action files to follow best practices.

---

## Ground Rules

- **Code of Conduct**: Be respectful and constructive. Reports: `info@civicinterconnect.org`.
- **License**: All contributions are accepted under the repo's **MIT License**.
- **Single Source of Truth**: The definitions are in `src/ci/transparency/spec/schemas/`. Documentation should not contradict these files.

---

## Before You Start

**Open an Issue or Discussion** for non-trivial changes so we can align early.

---

## Making Changes

- Follow **Semantic Versioning**:
  - **MAJOR**: breaking changes
  - **MINOR**: backwards-compatible additions
  - **PATCH**: clarifications/typos
- When things change, update related docs, examples, and `CHANGELOG.md`.

---

## Commit & PR guidelines

- **Small PRs**: one focused change per PR.
- **Titles**: start with area, e.g., `code: fix deprecation warning`.
- **Link** the Issue/Discussion when applicable.
- Prefer **squash merging** for a clean history.
- No DCO/CLA required.

---

## Questions / Support

- **Discussion:** For open-ended design questions.
- **Issue:** For concrete bugs or proposed text/schema changes.
- **Private contact:** `info@civicinterconnect.org` (for sensitive reports).

---

## DEV 1. Start Locally

**Mac/Linux/WSL**

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e ".[dev]"
pre-commit install
python3 scripts/generate_types.py
git add src/ci/transparency/types/
```

**Windows (PowerShell)**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip setuptools wheel
py -m pip install -e ".[dev]"
pre-commit install
py scripts\generate_types.py
git add src/ci/transparency/types/
```

## DEV 2. Validate Changes

1. Generate types first in case schema changed.
2. Add generated changes to git.
3. Commit updated types to git. 
4. Fix code formatting and linting.
5. Run precommit checks.
6. Build documentation to test.
7. Run tests.

```shell
py scripts\generate_types.py
git add src/ci/transparency/types/
git commit -m "Update generated types"
ruff format .
ruff check --fix .
pre-commit run --all-files
mkdocs build
pytest -q
```

2. Build and Verify Package

Mac/Linux/WSL (build, inspect)

```
python3 -m build
unzip -l dist/*.whl
```

Windows PowerShell (build, extract, clean up)

```
py -m build

$TMP = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("wheel_" + [System.Guid]::NewGuid())
Expand-Archive dist\*.whl -DestinationPath $TMP.FullName
Get-ChildItem -Recurse $TMP.FullName | ForEach-Object { $_.FullName.Replace($TMP.FullName + '\','') }
Remove-Item -Recurse -Force $TMP
```

## DEV 3. Preview Docs

```bash
mkdocs serve
```

Open: <http://127.0.0.1:8000/>

## DEV 4. Release

1. Update `CHANGELOG.md` with notable changes (beginning and end).
2. Update pyproject.toml with correct version "civic-transparency-spec==x.y.z",
3. Ensure all CI checks pass.
4. Build & verify package locally.
5. Tag and push (setuptools_scm uses the tag).

```bash
ruff format .
pre-commit run --all-files
git add .
git commit -m "Prep vx.y.z"
git push origin main

git tag vx.y.z -m "x.y.z"
git push origin vx.y.z
```

> A GitHub Action will **build**, **publish to PyPI** (Trusted Publishing), **create a GitHub Release** with artifacts, and **deploy versioned docs** with `mike`.

> You do **not** need to run `gh release create` or upload files manually.
