# Performance Benchmark

- **Python:** `3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)]`
- **orjson available:** `True`

## Validation Throughput (records/sec)

| Model | Records/sec |
|---|---:|
| PTag | 132,664 |
| PTagSeries (minimal) | 25,457 |
| PTagSeries (complex) | 243 |

## Serialization Throughput (records/sec)

| Model | Pydantic JSON | stdlib json | orjson |
|---|---:|---:|---:|
| PTag | 285,644 | 285,644 | 503,323 |
| PTagSeries (minimal) | 102,703 | 102,703 | 186,822 |
| PTagSeries (complex) | 1,598 | 1,598 | 2,670 |

## Estimated Memory Usage (bytes per object)

| Model | Bytes/object |
|---|---:|
| PTag | 1,790 |
| PTagSeries (minimal) | 8,340 |
| PTagSeries (complex) | 782,152 |
