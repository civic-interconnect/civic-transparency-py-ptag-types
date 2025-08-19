# Usage

This page shows common patterns for loading, validating, and serializing Civic Transparency types.

## Install

```bash
pip install "civic-transparency-types==0.2.*" "civic-transparency-spec==0.2.*"
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

## Validating with **jsonschema**

If you want an *extra* guardrail using the official schemas:

```python
import json
from importlib.resources import files
from jsonschema import Draft202012Validator

# 1) get the normative schema from the spec package
schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(schema_text)

# 2) validate the payload dict you produced with Pydantic
Draft202012Validator.check_schema(series_schema)          # sanity check the schema itself
Draft202012Validator(series_schema).validate(payload)     # raises jsonschema.ValidationError if invalid
```


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
The models are strict (`extra="forbid"`). Remove unexpected keys or update the schema definitions & regenerate.

**Datetime parsing**  
Use ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ` or with offset). Pydantic converts to `datetime`.

**Version mismatches**  
Pin both packages to compatible versions. If the definitions change, regenerate types.

---

## See also

- Schemas: <https://civic-interconnect.github.io/civic-transparency-spec/>
- API Reference:
  - [Series](reference/series.md)
  - [Provenance Tag](reference/provenance_tag.md)
