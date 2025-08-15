# Civic Transparency – Types

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-transparency-types/)
[![PyPI](https://img.shields.io/pypi/v/civic-transparency-types.svg)](https://pypi.org/project/civic-transparency-types/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](#)
[![CI Status](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml/badge.svg)](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **Typed Python models (Pydantic v2) for the Civic Transparency schema.**

> Maintained by [**Civic Interconnect**](https://github.com/civic-interconnect).

- **Docs (types):** https://civic-interconnect.github.io/civic-transparency-types/
- **Schemas & OpenAPI (spec):** https://civic-interconnect.github.io/civic-transparency-spec/
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## Install

```bash
pip install civic-transparency-types
```

> This package depends on `civic-transparency-spec` and uses its JSON Schemas to generate types.

---

## Quick Start

### Import canonical models

```python
from ci.transparency.types import Meta, Run, Scenario, Series, ProvenanceTag
```

Or import directly by module:

```python
from ci.transparency.types.series import Series
```

### Example: Build and validate a `Series`

```python
from ci.transparency.types import Series

series = Series(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",
    interval="minute",
    points=[]
)

# Validate using Pydantic (raises if invalid)
series.model_validate(series.model_dump())

# Serialize to JSON-compatible dict
payload = series.model_dump()
print(payload)
```

### Example: Validate against the JSON Schema (optional)

To validate against the canonical Draft-07 schema:

```python
import json
from importlib.resources import files
from jsonschema import Draft7Validator

schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(schema_text)

Draft7Validator.check_schema(series_schema)
Draft7Validator(series_schema).validate(payload)
```

---

## Regenerating Types (for contributors)

Types are generated using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator). To regenerate:

```bash
python scripts/generate_types.py
```

This rewrites `src/ci/transparency/types/*.py` and updates `__init__.py`.

---

## Versioning

- **SemVer**: Mirrors the version of the underlying schema in `civic-transparency-spec`.
- To ensure compatibility, pin both packages:

```bash
pip install "civic-transparency-types==0.1.*" "civic-transparency-spec==0.1.*"
```

---

## About

Civic Transparency is a shared data model for privacy-preserving, non-partisan insight into how content spreads online.
