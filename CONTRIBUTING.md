# CONTRIBUTING.md

This repo hosts the **Civic Transparency PTag Types** under the **MIT License**.
Goals: clarity, privacy-by-design, easy collaboration.

> tl;dr: Open an Issue/Discussion first for non-trivial changes, keep PRs small, and run the quick local checks.

---

## Ways to Contribute

- **Docs**: Improve narrative and examples in `docs/`.
- **Tooling**: Improve scripts and CI/CD.

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

## Local Dev with `uv`

### Prerequisites

- Python **3.12+** (3.13 supported)
- Git, VS Code (optional), and **[uv](https://github.com/astral-sh/uv)**

### One-time setup

```bash
uv python pin 3.12
uv venv
uv sync --extra dev --extra docs --upgrade
uv run pre-commit install
uv run .github/scripts/generate_types.py
uv run .github/scripts/verify_runtime.py
git add src/ci/transparency/ptag/types/
```

> **VS Code tip:** Do **not** set `python.analysis.*` overrides in `.vscode/settings.json`.
> Pyright is configured in `pyproject.toml`. If you see "settingsNotOverridable" warnings, remove those workspace overrides.
> Select the interpreter at `.venv` (Command Palette → "Python: Select Interpreter").

## Validate Local Changes

```bash
git pull
git add .
uv run ruff check . --fix
uv run ruff format .

uv run python .github/scripts/generate_types.py
git add ./src/ci/transparency/ptag/types/
```

```bash
uv run deptry .
uv run pyright
uv run pytest
uv run mkdocs build --strict
git commit -m "Update generated types"
```

Or run the project hooks (twice, if needed):

```bash
pre-commit run --all-files
git commit -m "Update generated types"
```

---

## Build and Verify Package

Mac/Linux/WSL (build, inspect)

```
uv build
unzip -l dist/*.whl
```

Windows PowerShell (build, extract, clean up)

```
uv build

$TMP = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("wheel_" + [System.Guid]::NewGuid())
Expand-Archive dist\*.whl -DestinationPath $TMP.FullName
Get-ChildItem -Recurse $TMP.FullName | ForEach-Object { $_.FullName.Replace($TMP.FullName + '\','') }
Remove-Item -Recurse -Force $TMP
```

---

## Docs

```bash
uv run mkdocs build --strict
uv run mkdocs serve
# Visit http://127.0.0.1:8000/
```

Ensure:

- Autodoc renders without errors
- Navigation works
- Examples render correctly

---

## Release

1. Update `CHANGELOG.md` with notable changes (beginning and end).
2. Update pyproject.toml with correct version in project dependencies "civic-transparency-ptag-spec>=x.y.z...",
3. Ensure all CI checks pass.
4. Build and verify package locally.
5. Tag and push (setuptools_scm uses the tag).

**Pre-release script:**

```bash
git add .
uv run ruff check . --fix
uv run ruff format .

pre-commit run --all-files
uv run pyright
uv run pytest
uv run mkdocs build --strict
uv build
```

```bash
git add .
git commit -m "Prep vx.y.z"
git push -u origin main

# Verify the GitHub actions run successfully. If so, continue:
git tag vx.y.z -m "x.y.z"
git push origin vx.y.z
```

A GitHub Action will:

- Build and publish to **PyPI** (Trusted Publishing),
- Create a **GitHub Release** with artifacts,
- Deploy **versioned docs** with `mike`.

## Cleanup

**Unix/macOS:**

```bash
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
rm -rf build/ dist/ .eggs/ src/*.egg-info/
```

**Windows PowerShell:**

```pwsh
Get-ChildItem -Recurse -Include __pycache__,*.egg-info,build,dist | Remove-Item -Recurse -Force
```
---

## Support

- **Discussions**: Open design questions
- **Issues**: Bugs or concrete proposals
- **Private**: `info@civicinterconnect.org` (sensitive reports)
