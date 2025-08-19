# Civic Transparency – Types

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-transparency-types/)
[![PyPI](https://img.shields.io/pypi/v/civic-transparency-types.svg)](https://pypi.org/project/civic-transparency-types/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](#)
[![CI Status](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml/badge.svg)](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **Typed Python models (Pydantic v2) for the Civic Transparency schema.**

> Maintained by [**Civic Interconnect**](https://github.com/civic-interconnect).

- **Documentation:** https://civic-interconnect.github.io/civic-transparency-types/
- **Schema Specification:** https://civic-interconnect.github.io/civic-transparency-spec/
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## Overview

This package provides strongly-typed Python models that correspond to the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/).
The types are automatically generated from canonical JSON Schema definitions, ensuring consistency and validation at runtime.

**Key Features:**
- **Type Safety:** Full Pydantic v2 validation with IDE support
- **Schema Compliance:** Generated directly from official JSON schemas
- **Privacy-First:** Designed for aggregated, non-PII data exchange
- **Interoperability:** JSON serialization/deserialization with validation

---

## Installation

```bash
pip install civic-transparency-types
```

For development or schema validation:
```bash
pip install "civic-transparency-types[dev]"
```

> **Note:** This package automatically includes the compatible `civic-transparency-spec` version as a dependency.

---

## Quick Start

### Basic Usage

```python
from ci.transparency.types import Series, ProvenanceTag

# Create a time series for civic data
series = Series(
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
from ci.transparency.types import Series

# Load from existing data with validation
series = Series.model_validate(data_dict)
series = Series.model_validate_json(json_string)

# Handle validation errors
from pydantic import ValidationError
try:
    invalid_series = Series.model_validate(bad_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Working with Provenance Tags

```python
from ci.transparency.types import ProvenanceTag

tag = ProvenanceTag(
    acct_age_bucket="1-6m",
    acct_type="person", 
    automation_flag="manual",
    post_kind="original",
    client_family="mobile",
    media_provenance="hash_only",
    dedup_hash="a1b2c3d4e5f6"
)
```

---

## Available Types

| Type | Description | Schema Source |
|------|-------------|---------------|
| `Series` | Privacy-preserving time series data for civic topics | `series.schema.json` |
| `ProvenanceTag` | Per-post metadata tags (bucketed, no PII) | `provenance_tag.schema.json` |

See the [API documentation](https://civic-interconnect.github.io/civic-transparency-types/api/) for complete field definitions and examples.

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
schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text()
schema = json.loads(schema_text)

# Validate your data
validator = Draft202012Validator(schema)
validator.validate(series.model_dump())
```

---

## Versioning Strategy

This package follows the underlying specification versions:
- **Major versions:** Breaking schema changes
- **Minor versions:** Backward-compatible additions  
- **Patch versions:** Documentation, tooling, bug fixes

**Best Practice:** Pin to compatible major versions:
```bash
pip install "civic-transparency-types>=1.0,<2.0"
```

The package automatically manages compatibility with the corresponding `civic-transparency-spec` version.

---

## Integration Examples

### FastAPI Integration
```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/civic-data")
async def receive_series(series: Series) -> dict:
    # Automatic validation and parsing
    return {"received": series.topic, "points": len(series.points)}
```

### File I/O
```python
from pathlib import Path
from ci.transparency.types import Series

# Save to file
series_file = Path("data.json")
series_file.write_text(series.model_dump_json(indent=2))

# Load from file
loaded_series = Series.model_validate_json(series_file.read_text())
```

---

## Development and Contributing

This is a **generated types package** - the source of truth is the [civic-transparency-spec](https://github.com/civic-interconnect/civic-transparency-spec) repository.

### For Type Users
- Report type-related issues here
- Request documentation improvements
- Share integration examples

### For Schema Changes
- Schema modifications should be made in the [spec repository](https://github.com/civic-interconnect/civic-transparency-spec)
- Types are automatically regenerated when the spec changes

### Local Development
```bash
git clone https://github.com/civic-interconnect/civic-transparency-types
cd civic-transparency-types
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

---

## Support and Community

- **Documentation:** https://civic-interconnect.github.io/civic-transparency-types/
- **Issues:** [GitHub Issues](https://github.com/civic-interconnect/civic-transparency-types/issues)
- **Discussions:** [GitHub Discussions](https://github.com/civic-interconnect/civic-transparency-types/discussions)  
- **Email:** info@civicinterconnect.org

---

## About Civic Transparency

Civic Transparency is an open standard for privacy-preserving, non-partisan analysis of how information spreads in civic contexts. The specification enables researchers, platforms, and civic organizations to share insights while protecting individual privacy.

**Core Principles:**
- **Privacy by Design:** No personally identifiable information
- **Aggregation First:** Time-bucketed, statistical summaries
- **Open Standard:** Collaborative, transparent development
- **Practical Implementation:** Real-world deployment focus
