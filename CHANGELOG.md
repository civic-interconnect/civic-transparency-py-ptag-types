# Changelog

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**  
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

## [Unreleased]

### Added
- (placeholder) Notes for the next release.

---

## [0.0.1] - 2025-08-11

### Added
- Initial public release of **Civic Transparency Types** (Pydantic v2) generated from `civic-transparency-spec==0.1.1`:
  - Models: `Meta`, `Run`, `Scenario`, `Series`, `ProvenanceTag`.
- **Docs site** scaffolding (MkDocs Material, i18n) with API reference pages via `mkdocstrings`.
- **Codegen script:** `scripts/generate_types.py` (uses `datamodel-code-generator`) to regenerate models from the spec schemas.
- **Testing:** Import/public API surface checks, version presence, and coverage target (pytest + pytest-cov).  
- **Packaging:** `py.typed` marker included for type checkers; generated modules shipped in the wheel.
- **CI:** GitHub Actions for lint, type regeneration guard, tests, docs build, and package build.

---

## Notes on versioning and releases

- We use **SemVer**:
  - **MAJOR** – breaking model changes relative to the spec
  - **MINOR** – backward-compatible additions
  - **PATCH** – clarifications, docs, tooling
- Versions are driven by git tags via `setuptools_scm`. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

[Unreleased]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.1...HEAD  
[0.0.1]: https://github.com/civic-interconnect/civic-transparency-types/releases/tag/v0.0.1
