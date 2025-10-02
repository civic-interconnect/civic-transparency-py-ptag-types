# API Reference

The Civic Transparency Types package provides a clean, typed interface to the Civic Transparency specification. All models are built with Pydantic v2 and automatically validate against the canonical JSON schemas.

## Package Overview

```python
import ci.transparency.ptag.types as ct

# Available models
ct.PTagSeries   # Time-bucketed civic data
ct.PTag         # Post metadata (privacy-preserving)

# Package metadata
ct.__version__     # Current package version
ct.__all__         # Public API surface
```

---

## Public API

### Core Models

| Class | Purpose | Schema Source |
|-------|---------|---------------|
| **`PTagSeries`** | Aggregated time series for civic topics | `ptag_series.schema.json` |
| **`PTag`** | Categorical post metadata (no PII) | `ptag.schema.json` |

### Package Information

- **`__version__`** (str): Current package version
- **`__all__`** (List[str]): Public API exports

---

## Import Patterns

### Recommended: Barrel Import
```python
from ci.transparency.ptag.types import PTagSeries, PTag

# Clean, simple imports for application code
series = PTagSeries(...)
tag = PTag(...)
```

### Alternative: Direct Module Import
```python
from ci.transparency.ptag.types.series import PTagSeries
from ci.transparency.ptag.types.ptag import PTag

# Useful for IDE "go to definition" and explicit dependencies
```

### Package-Level Import
```python
import ci.transparency.ptag.types as ct

# Namespaced access
series = ct.PTagSeries(...)
version = ct.__version__
```

---

## Base Model Behavior

All types inherit from `pydantic.BaseModel` and provide the complete Pydantic v2 API:

### Instance Methods

```python
series = PTagSeries(...)

# Serialization
data = series.model_dump()                      # dict (JSON-safe)
json_str = series.model_dump_json()             # JSON string
json_pretty = series.model_dump_json(indent=2)  # Pretty JSON

# Copying and updating
updated = series.model_copy(update={'topic': '#NewTopic'})
```

### Class Methods

```python
# Validation and parsing
series = PTagSeries.model_validate(data_dict)        # dict to PTagSeries
series = PTagSeries.model_validate_json(json_string) # JSON to PTagSeries

# Schema introspection
schema = PTagSeries.model_json_schema()              # Pydantic-generated schema
fields = PTagSeries.model_fields                     # Field definitions
```

### Configuration

All models use strict validation:
- **`extra="forbid"`**: Unknown fields are rejected
- **Type coercion**: Automatic type conversion where safe
- **Validation**: Full constraint checking (patterns, ranges, enums)

---

## Validation Features

### Runtime Type Safety

```python
from pydantic import ValidationError

try:
    # This will fail validation
    invalid_series = PTagSeries(
        topic="",  # Empty string not allowed
        generated_at="not-a-date",  # Invalid datetime
        interval="invalid",  # Not in enum
        points=[]
    )
except ValidationError as e:
    print(f"Validation errors: {e}")
```

### Enum Validation

```python
from ci.transparency.ptag.types import PTag

# Valid enum values are enforced
tag = PTag(
    acct_type="person",        # ✓ Valid
    automation_flag="manual"   # ✓ Valid
    # acct_type="wizard"       # ✗ Would raise ValidationError
)
```

### Pattern and Range Validation

```python
# String patterns, numeric ranges, etc. are validated
tag = PTag(
    dedup_hash="abc123",       # ✓ Valid hex pattern
    origin_hint="US-CA",       # ✓ Valid country-region format
    # dedup_hash="xyz!"        # ✗ Invalid characters
)
```

---

## Schema Access

### Pydantic Schema (Runtime)

```python
# Get Pydantic-generated schema for tooling
schema = PTagSeries.model_json_schema()
print(schema['properties']['topic'])  # Field definition
```

### Canonical Schema (Normative)

Access the official JSON schemas that define the specification:

```python
import json
from importlib.resources import files

# Get the source-of-truth schema
schema_text = files("ci.transparency.ptag.spec.schemas").joinpath(
    "series.schema.json"
).read_text("utf-8")
canonical_schema = json.loads(schema_text)

# Use for validation, documentation generation, etc.
from jsonschema import Draft202012Validator
validator = Draft202012Validator(canonical_schema)
validator.validate(series.model_dump())
```

---

## Serialization Details

### JSON Compatibility

```python
series = PTagSeries(...)

# These produce equivalent JSON-safe data
data1 = series.model_dump()
data2 = json.loads(series.model_dump_json())
assert data1 == data2
```

### Datetime Handling

```python
from datetime import datetime

series = PTagSeries(
    generated_at=datetime.now(),  # Accepts datetime objects
    # ...
)

# Serializes to ISO 8601 strings
data = series.model_dump()
assert isinstance(data['generated_at'], str)  # "2025-01-15T12:00:00Z"
```

### Field Customization

```python
# Exclude fields during serialization
public_data = series.model_dump(exclude={'generated_at'})

# Include only specific fields
minimal_data = series.model_dump(include={'topic', 'interval'})

# Use aliases if defined (none currently in this spec)
aliased_data = series.model_dump(by_alias=True)
```

---

## Error Handling

### Validation Errors

```python
from pydantic import ValidationError

def safe_parse_series(data: dict) -> PTagSeries | None:
    """Parse series data with error handling."""
    try:
        return PTagSeries.model_validate(data)
    except ValidationError as e:
        # Log specific validation failures
        for error in e.errors():
            field = " → ".join(str(loc) for loc in error['loc'])
            print(f"Validation error in {field}: {error['msg']}")
        return None
```

### Field-Level Errors

```python
try:
    PTagSeries.model_validate(bad_data)
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc']}")       # Which field failed
        print(f"Value: {error['input']}")     # The invalid input
        print(f"Error: {error['msg']}")       # What went wrong
        print(f"Type: {error['type']}")       # Error category
```

---

## Framework Integration

### FastAPI

Automatic request/response validation:

```python
from fastapi import FastAPI
from ci.transparency.ptag.types import PTagSeries

app = FastAPI()

@app.post("/data")
async def receive_data(series: PTagSeries) -> dict:
    # 'series' is automatically validated
    return {"received": series.topic}
```

### Dataclasses Integration

```python
from dataclasses import dataclass
from ci.transparency.ptag.types import PTagSeries

@dataclass
class ProcessingResult:
    series: PTagSeries
    processed_at: str

    def to_dict(self):
        return {
            'series': self.series.model_dump(),
            'processed_at': self.processed_at
        }
```

### Django Models

```python
from django.db import models
from ci.transparency.ptag.types import PTagSeries
import json

class CivicDataRecord(models.Model):
    topic = models.CharField(max_length=255)
    data = models.JSONField()

    def get_series(self) -> PTagSeries:
        return PTagSeries.model_validate(self.data)

    def set_series(self, series: PTagSeries):
        self.topic = series.topic
        self.data = series.model_dump()
```

---

## Type Information

### Static Type Checking

The package includes `py.typed` for full mypy/pyright support:

```python
from ci.transparency.ptag.types import PTagSeries

def process_series(series: PTagSeries) -> str:
    # Full type safety and IDE completion
    return series.topic.upper()

# mypy will catch type errors
process_series("not a series")  # Error: Argument 1 has incompatible type
```

### Runtime Type Inspection

```python
from ci.transparency.ptag.types import PTagSeries
import inspect

# Inspect model structure
print(PTagSeries.__annotations__)  # Field type annotations
print(PTagSeries.model_fields)     # Pydantic field definitions

# Check inheritance
assert issubclass(PTagSeries, BaseModel)
```
