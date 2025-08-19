# Civic Transparency – Types (Python)

Strongly-typed Python models for the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/), built with Pydantic v2.

## What This Package Provides

- **Runtime Type Safety:** Full validation of civic transparency data structures
- **IDE Support:** Complete type hints and autocompletion
- **Schema Compliance:** Generated directly from canonical JSON schemas
- **Privacy Compliance:** Built-in validation for privacy-preserving data patterns

## Installation

```bash
pip install civic-transparency-types
```

## Quick Example

```python
from ci.transparency.types import Series
from datetime import datetime

# Create a validated civic data series
series = Series(
    topic="#CityBudget2025",
    generated_at=datetime.now().isoformat() + "Z",
    interval="minute",
    points=[]  # Your aggregated, privacy-preserving data points
)

# Automatic validation ensures schema compliance
validated_data = series.model_dump()  # Safe for JSON serialization
```

## Key Features

### Type Safety
All models enforce the Civic Transparency schema constraints at runtime:
- Enum validation for categorical fields
- Date/time format validation (ISO 8601)
- Numeric range and string pattern validation
- Required field enforcement

### Privacy by Design
The type system enforces privacy-preserving patterns:
- No direct identifiers allowed
- Bucketed categorical values (e.g., account age ranges)
- Aggregated statistical summaries only
- Deduplication hashes instead of content

### Easy Integration
Works seamlessly with modern Python tooling:
- **FastAPI:** Automatic request/response validation
- **Dataclasses:** Compatible with existing data structures  
- **JSON APIs:** Native serialization/deserialization
- **Testing:** Clear validation error messages

## Available Types

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **Series** | Time-bucketed aggregated data | `topic`, `points`, `interval` |
| **ProvenanceTag** | Post metadata (no PII) | `acct_type`, `automation_flag`, `media_provenance` |

## See Also

- **[API Reference](api.md):** Complete type documentation
- **[Series Reference](reference/series.md):** Detailed field documentation
- **[Provenance Tag Reference](reference/provenance_tag.md):** Metadata field guide
- **[Performance Guide](performance.md):** Performance guide
- **[Usage Guide](usage.md):** Common patterns and examples

## Relationship to Specification

This package provides the **runtime implementation** of types defined in the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/).
The types are automatically generated from the canonical JSON schemas, ensuring perfect alignment with the specification.

For schema definitions, OpenAPI documentation, and specification details, visit the [spec repository](https://civic-interconnect.github.io/civic-transparency-spec/).
