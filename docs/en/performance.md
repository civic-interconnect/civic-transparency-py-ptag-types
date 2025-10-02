# Performance Guide

The Civic Transparency PTag Types are designed for high-throughput validation and efficient serialization.

## Baseline

Performance is measured continuously in CI using `benchmark_performance.py`.

- **Validation throughput**: PTag ~160K/sec, PTagSeries (minimal) ~25K/sec
- **Serialization**: Pydantic’s built-in JSON is ~2–3× faster than stdlib `json`
- **Memory footprint**: PTag ~1KB, PTagSeries ranges from ~7KB (minimal) to ~660KB (100 points)

## Latest Results

See the full benchmark outputs:

- [performance_results.txt](https://github.com/civic-interconnect/civic-transparency-py-ptag-types/blob/main/performance_results.txt)
- [performance_results.md](https://github.com/civic-interconnect/civic-transparency-py-ptag-types/blob/main/performance_results.md)

Performance result files are generated automatically and numbers may vary depending on hardware, OS, and Python version.

---

**Note:** For production scenarios, start with `PTag` for metadata-heavy tasks (very fast), and use streaming/serialization strategies for large `PTagSeries`.
