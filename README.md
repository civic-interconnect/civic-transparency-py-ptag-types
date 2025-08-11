# Civic Transparency - Types

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-transparency-types/)
[![PyPI](https://img.shields.io/pypi/v/civic-transparency-types.svg)](https://pypi.org/project/civic-transparency-types/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](#)
[![CI Status](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml/badge.svg)](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **Typed Python models (Pydantic v2) for the Civic Transparency specification.**  

> Maintained by **[Civic Interconnect](https://github.com/civic-interconnect)**.

- **Docs (types):** https://civic-interconnect.github.io/civic-transparency-types/
- **Spec (schemas/OpenAPI):** https://civic-interconnect.github.io/civic-transparency-spec/
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)


## Install

```bash
pip install civic-transparency-types
# OR Pin version
pip install "civic-transparency-spec==0.1.1"
```

> This package depends on `civic-transparency-spec` and is generated from its JSON Schemas.



## Quick start

### Import the canonical models

```python
from ci.transparency.types import Meta, Run, Scenario, Series, ProvenanceTag
```

Or use per-module imports:

```python
from ci.transparency.types.meta import Meta
from ci.transparency.types.run import Run
from ci.transparency.types.scenario import Scenario
from ci.transparency.types.series import Series
from ci.transparency.types.provenance_tag import ProvenanceTag
```

### Example: build & validate a `Series`

```python
from ci.transparency.types import Series

series = Series(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",
    interval="minute",
    points=[]
)

# Pydantic v2 validation happens on init; raise if invalid:
series.model_validate(series.model_dump())

# Serialize to JSON-friendly dict
payload = series.model_dump()
print(payload)
```

### Example: validate against the JSON Schemas (optional)

If you also want to validate against the **normative** Draft-07 schemas shipped in `civic-transparency-spec`:

```python
import json
from importlib.resources import files
from jsonschema import Draft7Validator

schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(schema_text)

Draft7Validator.check_schema(series_schema)
Draft7Validator(series_schema).validate(payload)  # raises if invalid
```

---

## Regenerating types (contributors)

Types are generated from `civic-transparency-spec` using `datamodel-code-generator`. Run:

```bash
python scripts/generate_types.py
```

This rewrites `src/ci/transparency/types/*.py` and updates `__init__.py` exports.

---

## Versioning

- **SemVer**: follow the spec’s versions; types stay compatible with the corresponding `civic-transparency-spec`.
- Pin both for reproducibility in clients, e.g.:
  ```bash
  pip install "civic-transparency-types==0.0.X" "civic-transparency-spec==0.0.X"
  ```

---

## About

Civic Transparency is an open specification for privacy-preserving, non-partisan visibility into **how** content spreads online (not what it says).  
