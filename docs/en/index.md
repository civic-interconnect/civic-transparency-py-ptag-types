# Civic Transparency – Types (Python)

Typed Python models for the Civic Transparency Schema Definitions (Pydantic v2).

## Install

```bash
pip install civic-transparency-types
```

## Quick Start

```python
from ci.transparency.types import Series

series = Series(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",  # ISO 8601; parsed to datetime
    interval="minute",
    points=[],  # add your time-bucketed data here
)
print(series.model_dump())  # dict ready to JSON-serialize
```

**Pydantic validation example** (what happens on bad input):

```python
from ci.transparency.types import Meta
from pydantic import ValidationError

try:
    Meta(topic="ok", window={"start": "2026-02-01T00:00:00Z"})  # missing 'end'
except ValidationError as e:
    print(e)
```

## What you get

- **Typed models**: `Meta`, `Run`, `Scenario`, `Series`, `ProvenanceTag`
- **Validation**: Pydantic v2 enforces schema constraints (formats, enums, min/max, patterns)
- **Interop**: `.model_dump()` for JSON, `.model_validate()` to load/validate existing data

## API Reference

- [Meta](reference/meta.md)
- [Run](reference/run.md)
- [Scenario](reference/scenario.md)
- [Series](reference/series.md)
- [Provenance Tag](reference/provenance_tag.md)

## Versioning

These types are **generated from the Civic Transparency Schema Definitions**. Keep your project pinned to a compatible versions set (e.g., `civic-transparency-types==0.1.x`) to avoid unexpected breaking changes.
