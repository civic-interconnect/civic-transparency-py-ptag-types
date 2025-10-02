# Usage


Install (update version as needed):


```bash
pip install "civic-transparency-py-ptag-types==0.2.5"
```

---

## Example

```python
from ci.transparency.ptag.types import PTagSeries

series = PTagSeries(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",  # parsed to datetime
    interval="minute",
    points=[],
)

# Serialize
text = series.model_dump_json(indent=2)

# Deserialize / validate
loaded = PTagSeries.model_validate_json(text)
```

---

## Extra Validation

```python
import json
from importlib.resources import files
from jsonschema import Draft202012Validator

schema = json.loads(
    files("ci.transparency.ptag.spec.schemas")
    .joinpath("series.schema.json")
    .read_text("utf-8")
)
Draft202012Validator(schema).validate(series.model_dump())

```

---

## Notes

- Models are strict (extra="forbid").
- Datetimes must be ISO 8601.
- Pin both the spec and types packages for compatibility.

---

## See also

- Schemas: <https://civic-interconnect.github.io/civic-transparency-ptag-spec/>
- Types API:
  - [PTagSeries](./api/ptag_series.md)
  - [TTag](./api/ptag.md)
