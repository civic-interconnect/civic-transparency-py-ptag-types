# Civic Transparency – Types

[![CI Status](https://github.com/civic-interconnect/civic-transparency-py-ptag-types/actions/workflows/ci.yml/badge.svg)](https://github.com/civic-interconnect/civic-transparency-py-ptag-types/actions/workflows/ci.yml)
[![Docs: latest](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://civic-interconnect.github.io/civic-transparency-py-ptag-types/)
[![PyPI version](https://img.shields.io/pypi/v/civic-transparency-ptag-types.svg)](https://pypi.org/project/civic-transparency-ptag-types/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Python: 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **Typed Python models (Pydantic v2) for the Civic Transparency PTag schema.**

---

## Overview

This package provides strongly-typed Python models that correspond to the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-ptag-spec/).
The types are automatically generated from canonical JSON Schema definitions, ensuring consistency and validation at runtime.

**Key Features:**

- **Type Safety:** Full Pydantic v2 validation with IDE support
- **Schema Compliance:** Generated directly from official JSON schemas
- **Privacy-First:** Designed for aggregated, non-PII data exchange
- **Interoperability:** JSON serialization/deserialization with validation

---

## Available Types

| Type            | Description                                          | Schema Source                |
| --------------- | ---------------------------------------------------- | ---------------------------- |
| `PTagSeries`        | Privacy-preserving time series data for civic topics | `series.schema.json`         |
| `PTag` | Per-post metadata tags (bucketed, no PII)            | `ptag.schema.json` |

See the [API documentation](https://civic-interconnect.github.io/civic-transparency-py-ptag-types/api/) for complete field definitions and examples.

---

## Installation

```bash
pip install civic-transparency-py-ptag-types
```

> **Note:** This package automatically includes the compatible `civic-transparency-ptag-spec` version as a dependency.

---

## Quick Start

### Basic Usage

```python
from ci.transparency.ptag.types import PTagSeries, PTag

# Create a time series for civic data
series = PTagSeries(
    topic="#LocalElection",
    generated_at="2025-01-15T12:00:00Z",
    interval="minute",
    points=[]  # Add your aggregated data points here
)

# Validate and serialize
data = series.model_dump()  # JSON-compatible dict
json_str = series.model_dump_json(indent=2)  # Pretty JSON string
```

### Loading and Validation

```python
from ci.transparency.ptag.types import PTagSeries

# Load from existing data with validation
series = PTagSeries.model_validate(data_dict)
series = PTagSeries.model_validate_json(json_string)

# Handle validation errors
from pydantic import ValidationError
try:
    invalid_series = PTagSeries.model_validate(bad_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Working with PTags (Provenance Tags)

```python
from ci.transparency.ptag.types import PTag

tag = PTag(
    acct_age_bucket="1-6m",
    acct_type="person",
    automation_flag="manual",
    post_kind="original",
    client_family="mobile",
    media_provenance="hash_only",
    dedup_hash="a1b2c3d4"
)
```

---

## Validation and Schemas

### Pydantic Validation

All models use Pydantic v2 for runtime validation:

- **Strict typing:** Unknown fields are rejected
- **Format validation:** ISO 8601 dates, patterns, enums
- **Range checking:** Min/max values, string lengths
- **Nested validation:** Complex object hierarchies

### JSON Schema Validation (Optional)

For additional validation against the canonical schemas:

```python
import json
from importlib.resources import files
from jsonschema import Draft202012Validator

# Get the official schema
schema_text = files("ci.transparency.ptag.spec.schemas").joinpath("series.schema.json").read_text()
schema = json.loads(schema_text)

# Validate your data
validator = Draft202012Validator(schema)
validator.validate(series.model_dump())
```

---

## Versioning Strategy

The package automatically manages compatibility with the corresponding `civic-transparency-ptag-spec` version.

---

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI
from ci.transparency.ptag.types import PTagSeries

app = FastAPI()

@app.post("/civic-data")
async def receive_series(series: PTagSeries) -> dict:
    # Automatic validation and parsing
    return {"received": series.topic, "points": len(series.points)}
```

### File I/O

```python
from pathlib import Path
from ci.transparency.ptag.types import PTagSeries

# Save to file
series_file = Path("data.json")
series_file.write_text(series.model_dump_json(indent=2))

# Load from file
loaded_series = PTagSeries.model_validate_json(series_file.read_text())
```

---

## Performance Benchmarks

See the latest benchmark results in
[performance_results.md](./performance_results.md).

---

## Development and Contributing

This is a **generated types package** - the source of truth is the [civic-transparency-ptag-spec](https://github.com/civic-interconnect/civic-transparency-ptag-spec) repository.

### For Type Users

- Report type-related issues here
- Request documentation improvements
- Share integration examples

### For Schema Changes

- Schema modifications should be made in the [spec repository](https://github.com/civic-interconnect/civic-transparency-ptag-spec)
- Types are automatically regenerated when the spec changes

### Local Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## Versioning

This specification follows semantic versioning.
See [CHANGELOG.md](./CHANGELOG.md) for version history.

## License

MIT © [Civic Interconnect](https://github.com/civic-interconnect)
