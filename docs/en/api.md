# API

Typed models reflect the Civic Transparency schemas and are exposed via a single public package:

```python
import ci.transparency.types as ct
ct.__all__  # -> ["Meta", "Run", "Scenario", "Series", "ProvenanceTag"]
ct.__version__  # string, set by setuptools-scm
```

## Package overview

- **`ci.transparency.spec`**: Normative Draft-07 JSON Schemas and OpenAPI definitions.
- **`ci.transparency.types`**: Runtime model layer using Pydantic, backed by JSON Schemas.
  

## Public modules / classes

- **`ci.transparency.types`** (barrel module)
  - `Meta`
  - `Run`
  - `Scenario`
  - `Series`
  - `ProvenanceTag`
  - `__version__` (string)

> The concrete fields come directly from the JSON Schemas. See per-class reference:
> - [Meta](reference/meta.md)
> - [Run](reference/run.md)
> - [Scenario](reference/scenario.md)
> - [Series](reference/series.md)
> - [Provenance Tag](reference/provenance_tag.md)

---

## Base behavior (Pydantic v2)

All models inherit from `pydantic.BaseModel` and therefore support the standard API:

```python
m = ct.Series(...)
m.model_dump()           # -> dict (JSON-ready)
m.model_dump_json()      # -> JSON string
m.model_copy(update={})  # shallow copy w/ updates
m.model_json_schema()    # JSON Schema derived from the model
type(m).model_validate(obj)         # validate existing dict
type(m).model_validate_json(bytes)  # validate JSON string/bytes
```

### Validation & strictness

- **Types follow the schema definitions:** for example, a property with "format": "date-time" becomes a datetime field in Python.
- **Unknown fields** are rejected (`extra="forbid"`).
- **Enums / patterns / min/max** from the schema definitions are enforced by Pydantic at runtime.

```python
from pydantic import ValidationError

try:
    ct.ProvenanceTag(acct_type="wizard")  # not in enum
except ValidationError as e:
    print(e)
```

### Serialization

- `.model_dump()` returns plain Python types (safe for `json.dumps`).
- `.model_dump_json()` returns a string using Pydantic’s encoder (datetimes to ISO 8601, etc.).
- Use `by_alias=True` if you later add field aliases.

### JSON Schema (for tool integration)

If you need a Pydantic-generated JSON Schema for a specific model:

```python
schema = ct.Series.model_json_schema()
```

> Note: this Pydantic-generated schema is useful for tooling, but the **normative** definitions live in the `civic-transparency-spec` package (Draft-07). If you must validate against the normative definitions, see **Usage / Validating with jsonschema**.

---

## Accessing the **Schema Definitions**

The normative JSON Schemas ship in the `civic-transparency-spec` package:

```python
import json
from importlib.resources import files

text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(text)
```

You can then validate payloads with `jsonschema` (see examples in **Usage**).

---

## Versioning

- This package tracks the schema definitions closely. Pin compatible versions for reproducibility:
  ```bash
  pip install "civic-transparency-types==0.1.*" "civic-transparency-spec==0.1.*"
  ```
- `ci.transparency.types.__version__` exposes the installed package version string.

---

## Import patterns

Barrel import (recommended):

```python
from ci.transparency.types import Series, Meta, Run, Scenario, ProvenanceTag
```

Per-module import (helpful for IDE "go to definition"):

```python
from ci.transparency.types.series import Series
```

