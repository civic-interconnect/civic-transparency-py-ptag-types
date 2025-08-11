# Usage

This page shows common patterns for loading, validating, and serializing Civic Transparency types.

## Install

```bash
pip install civic-transparency-types
# (optional, recommended) pin alongside the spec
pip install "civic-transparency-types==0.1.*" "civic-transparency-spec==0.1.*"
```

---

## Create and validate

```python
from ci.transparency.types import Series

series = Series(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",  # parsed to datetime
    interval="minute",
    points=[],
)
```

If any field violates the spec (enum, pattern, required, etc.), Pydantic raises `ValidationError`.

```python
from pydantic import ValidationError
from ci.transparency.types import Meta

try:
    Meta(  # 'window.end' missing, will fail
        topic="topic",
        window={"start": "2026-02-01T00:00:00Z"},
        notes=None,
        seed=0,
        accounts_generated=0,
        posts_raw=0,
        buckets_aggregated=0,
        scenario_file="scenario.yaml",
        scenario_sha256="0"*64,
        events=[],
    )
except ValidationError as e:
    print(e)
```

---

## Serialize / deserialize

To send/store:

```python
payload: dict = series.model_dump()         # JSON-friendly dict
text: str = series.model_dump_json(indent=2)
```

To load an existing dict/JSON and validate:

```python
from ci.transparency.types import Series

loaded = Series.model_validate(payload)         # dict -> Series
loaded2 = Series.model_validate_json(text)      # JSON -> Series
```

---

## Validating with **jsonschema** (normative spec)

If you want an *extra* guardrail using the official Draft-07 schemas:

```python
import json
from importlib.resources import files
from jsonschema import Draft7Validator

# 1) get the normative schema from the spec package
schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(schema_text)

# 2) validate the payload dict you produced with Pydantic
Draft7Validator.check_schema(series_schema)          # sanity check the schema itself
Draft7Validator(series_schema).validate(payload)     # raises jsonschema.ValidationError if invalid
```

> In practice, Pydantic’s validation should already match the spec. This step is optional and mostly useful for CI or cross-language parity.

---

## Round-trip file I/O

```python
import json
from pathlib import Path
from ci.transparency.types import Series

out = Path("series.json")

# write
out.write_text(Series(...).model_dump_json(indent=2), encoding="utf-8")

# read + validate
data = json.loads(out.read_text(encoding="utf-8"))
series = Series.model_validate(data)
```

---

## Using with FastAPI (optional)

Pydantic v2 models work out-of-the-box:

```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/series")
def post_series(s: Series) -> Series:
    # s is validated already
    return s  # echo back, or transform and return
```

---

## Generating / Regenerating the types (contributors)

Types are generated from the `civic-transparency-spec` package with `datamodel-code-generator`.

```bash
# in the types repo
python scripts/generate_types.py
```

CI tip (to ensure generated code is up to date):

```bash
python scripts/generate_types.py
git diff --exit-code
```

---

## Troubleshooting

**“Unknown field …”**  
The models are strict (`extra="forbid"`). Remove unexpected keys or update the spec & regenerate.

**Datetime parsing**  
Use ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ` or with offset). Pydantic converts to `datetime`.

**Version mismatches**  
Pin both packages to compatible `0.1.*` versions. If the spec updates fields/enums, regenerate types.

---

## See also

- Spec & Schemas: <https://civic-interconnect.github.io/civic-transparency-spec/>
- API Reference:
  - [Meta](reference/meta.md)
  - [Run](reference/run.md)
  - [Scenario](reference/scenario.md)
  - [Series](reference/series.md)
  - [Provenance Tag](reference/provenance_tag.md)
