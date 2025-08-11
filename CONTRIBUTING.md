# CONTRIBUTING.md

This repo hosts the **Civic Transparency Types** under the **MIT License**.
Our goals are clarity, privacy-by-design, and low friction for collaborators.

> tl;dr: open an Issue or Discussion first for anything non-trivial, keep PRs small and focused, and please run the quick local checks below.

---

## Ways to Contribute

- **Docs**: Fix typos, clarify definitions, or improve examples in `docs/en/**`.
- **Spec**: Propose changes to the spec text, normative notes, or privacy language.
- **Schemas**: Add or adjust JSON Schemas or the OpenAPI file in `src/ci/transparency/spec/schemas/`.
- **CWEs**: Contribute new transparency pitfalls under `docs/en/docs/cwe/`.

---

## Ground Rules

- **Code of Conduct**: Be respectful and constructive. Reports: `info@civicinterconnect.org`.
- **License**: All contributions are accepted under the repo's **MIT License**.
- **Single Source of Truth**: The normative artifacts are in `src/ci/transparency/spec/schemas/`. Documentation should not contradict these files.


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
```

**Windows (PowerShell)**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip setuptools wheel
py -m pip install -e ".[dev]"
pre-commit install
py scripts\generate_types.py
```

## DEV 2. Validate Changes

Run all checks.

```shell
mkdocs build
pre-commit run --all-files
pytest -q

## DEV 3. Preview Docs

```bash
mkdocs serve
```

Open: <http://127.0.0.1:8000/>

## DEV 4. Release

1. Update `CHANGELOG.md` with notable changes.
2. Ensure all CI checks pass.
3. Build & verify package locally.
4. Tag and push (setuptools_scm uses the tag).

```bash
git add .
git commit -m "Prep v0.0.5"
git push origin main

git tag v0.0.5 -m "0.0.5"
git push origin v0.0.5
```

> A GitHub Action will **build**, **publish to PyPI** (Trusted Publishing), **create a GitHub Release** with artifacts, and **deploy versioned docs** with `mike`.  

> You do **not** need to run `gh release create` or upload files manually.

