#!/usr/bin/env python3
"""Benchmark script for civic-transparency-py-ptag-types performance.

Run this to get actual performance characteristics for your models.

"""

from datetime import UTC, datetime
import json
from pathlib import Path
import statistics
import sys
import time
import tracemalloc
from typing import Any

from pydantic import BaseModel

try:
    import orjson

    has_orjson = True
except ImportError:
    has_orjson = False

from ci.transparency.ptag.types import PTag, PTagSeries


def create_minimal_series() -> dict[str, Any]:
    """Create minimal valid PTagSeries data."""
    return {
        "topic": "#BenchmarkTopic",
        "generated_at": "2025-08-19T12:00:00Z",
        "interval": "minute",
        "points": [
            {
                "interval_start": "2025-08-19T12:00:00Z",
                "volume": 100,
                "reshare_ratio": 0.25,
                "recycled_content_rate": 0.1,
                "acct_age_mix": {
                    "0-7d": 0.2,
                    "8-30d": 0.3,
                    "1-6m": 0.3,
                    "6-24m": 0.15,
                    "24m+": 0.05,
                },
                "automation_mix": {
                    "manual": 0.8,
                    "scheduled": 0.1,
                    "api_client": 0.05,
                    "declared_bot": 0.05,
                },
                "client_mix": {"web": 0.6, "mobile": 0.35, "third_party_api": 0.05},
                "coordination_signals": {
                    "burst_score": 0.3,
                    "synchrony_index": 0.2,
                    "duplication_clusters": 5,
                },
            }
        ],
    }


def create_complex_series(num_points: int = 100) -> dict[str, Any]:
    """Create PTagSeries data with many points."""
    base_data = create_minimal_series()
    base_point = base_data["points"][0]

    # Generate many time points
    points = []
    for i in range(num_points):
        point = base_point.copy()
        # Vary timestamp
        ts = datetime(2025, 8, 19, 12, i % 60, 0, tzinfo=UTC)
        point["interval_start"] = ts.isoformat().replace("+00:00", "Z")
        # Vary some values slightly
        point["volume"] = 100 + (i % 50)
        point["reshare_ratio"] = min(1.0, 0.25 + (i % 10) * 0.05)
        points.append(point)

    base_data["points"] = points
    return base_data


def create_ptag() -> dict[str, Any]:
    """Create minimal valid PTag data."""
    return {
        "acct_age_bucket": "1-6m",
        "acct_type": "person",
        "automation_flag": "manual",
        "post_kind": "original",
        "client_family": "mobile",
        "media_provenance": "hash_only",
        "origin_hint": "US-CA",
        "dedup_hash": "a1b2c3d4",
    }


def benchmark_validation(
    name: str,
    model_class: type[BaseModel],
    data: dict[str, Any],
    iterations: int = 10000,
):
    """Benchmark validation performance."""
    print(f"\n🔬 Benchmarking {name} validation ({iterations:,} iterations)")

    # Warm up
    for _ in range(100):
        model_class.model_validate(data)

    # Memory tracking
    tracemalloc.start()

    # Timing
    times: list[float] = []
    for _ in range(5):  # 5 runs for statistics
        start_time = time.perf_counter()
        for _ in range(iterations):
            obj = model_class.model_validate(data)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    # Memory measurement
    tracemalloc.stop()

    # Calculate stats
    avg_time: float = statistics.mean(times)
    std_time: float = statistics.stdev(times)
    records_per_sec = iterations / avg_time

    print(f"  Average time: {avg_time:.4f}s (±{std_time:.4f}s)")
    print(f"  Records/sec: {records_per_sec:,.0f}")
    print(f"  Time per record: {(avg_time / iterations) * 1000:.3f}ms")

    return records_per_sec, obj


def benchmark_serialization(name: str, obj, iterations: int = 10000) -> dict[str, float]:
    """Benchmark serialization performance."""
    print(f"\n📤 Benchmarking {name} serialization ({iterations:,} iterations)")

    results = {}

    # Pydantic JSON
    times: list[float] = []
    for _ in range(5):
        start_time = time.perf_counter()
        for _ in range(iterations):
            json.dumps(obj.model_dump(mode="json"))
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    avg_time = statistics.mean(times)
    results["pydantic"] = iterations / avg_time
    print(f"  Pydantic JSON: {results['pydantic']:,.0f} records/sec")

    # model_dump() + stdlib json (need mode='json' for enum serialization)
    times = []
    for _ in range(5):
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = obj.model_dump(mode="json")  # This converts enums to their values
            json.dumps(data)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    avg_time = statistics.mean(times)
    results["stdlib_json"] = iterations / avg_time
    print(f"  stdlib json: {results['stdlib_json']:,.0f} records/sec")

    # orjson if available
    if has_orjson:
        times = []
        for _ in range(5):
            start_time = time.perf_counter()
            for _ in range(iterations):
                data = obj.model_dump(mode="json")  # Convert enums for orjson too
                orjson.dumps(data)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        results["orjson"] = iterations / avg_time
        print(f"  orjson: {results['orjson']:,.0f} records/sec")

    return results


def measure_memory_usage(name: str, obj):
    """Measure memory usage of objects."""
    print(f"\n💾 Memory usage for {name}")

    # Get object size
    import sys

    size = sys.getsizeof(obj)

    # More detailed measurement
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    # Create a list of objects to measure overhead
    _: list[type(obj)] = [type(obj).model_validate(obj.model_dump()) for _ in range(1000)]

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot2.compare_to(snapshot1, "lineno")
    total_memory = sum(stat.size for stat in top_stats)
    avg_per_object = total_memory / 1000

    print(f"  sys.getsizeof(): {size:,} bytes")
    print(f"  Estimated per object: {avg_per_object:,.0f} bytes")
    print(f"  JSON size: {len(obj.model_dump_json()):,} bytes")

    return avg_per_object


# ADD these helpers anywhere above main()


def _repo_root() -> Path:
    # script is in .github/scripts/, so go up two levels
    return Path(__file__).resolve().parents[2]


def _write_text_summary(
    *,
    ptag_rps: float,
    series_min_rps: float,
    series_complex_rps: float,
    ptag_ser_pyd: float,
    series_min_ser_pyd: float,
    series_complex_ser_pyd: float,
    ptag_ser_orj: float | None,
    series_min_ser_orj: float | None,
    series_complex_ser_orj: float | None,
    ptag_mem: float,
    series_min_mem: float,
    series_complex_mem: float,
) -> Path:
    lines = []
    lines.append("PERFORMANCE SUMMARY")
    lines.append("=" * 50)
    lines.append("")
    lines.append("  VALIDATION PERFORMANCE")
    lines.append(f"PTag:      {ptag_rps:,.0f} records/sec")
    lines.append(f"PTagSeries (minimal):    {series_min_rps:,.0f} records/sec")
    lines.append(f"PTagSeries (complex):       {series_complex_rps:,.0f} records/sec")
    lines.append("")
    lines.append("  SERIALIZATION PERFORMANCE (Pydantic JSON)")
    lines.append(f"PTag:      {ptag_ser_pyd:,.0f} records/sec")
    lines.append(f"PTagSeries (minimal):   {series_min_ser_pyd:,.0f} records/sec")
    lines.append(f"PTagSeries (complex):     {series_complex_ser_pyd:,.0f} records/sec")
    if ptag_ser_orj is not None:
        lines.append("")
        lines.append("  SERIALIZATION PERFORMANCE (orjson)")
        lines.append(f"PTag:      {ptag_ser_orj:,.0f} records/sec")
        lines.append(f"PTagSeries (minimal):   {series_min_ser_orj:,.0f} records/sec")
        lines.append(f"PTagSeries (complex):     {series_complex_ser_orj:,.0f} records/sec")
    lines.append("")
    lines.append("  MEMORY USAGE")
    lines.append(f"PTag:        {ptag_mem:,.0f} bytes")
    lines.append(f"PTagSeries (minimal):     {series_min_mem:,.0f} bytes")
    lines.append(f"PTagSeries (complex):   {series_complex_mem:,.0f} bytes")

    out = _repo_root() / "performance_results.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _write_markdown_summary(
    *,
    python_version: str,
    has_orjson: bool,
    ptag_rps: float,
    series_min_rps: float,
    series_complex_rps: float,
    ptag_ser_pyd: float,
    series_min_ser_pyd: float,
    series_complex_ser_pyd: float,
    ptag_ser_orj: float | None,
    series_min_ser_orj: float | None,
    series_complex_ser_orj: float | None,
    ptag_mem: float,
    series_min_mem: float,
    series_complex_mem: float,
) -> Path:
    def fmt(n: float | None) -> str:
        return f"{n:,.0f}" if n is not None else "—"

    lines = []
    lines.append("# Performance Benchmark")
    lines.append("")
    lines.append(f"- **Python:** `{python_version.strip()}`")
    lines.append(f"- **orjson available:** `{has_orjson}`")
    lines.append("")
    lines.append("## Validation Throughput (records/sec)")
    lines.append("")
    lines.append("| Model | Records/sec |")
    lines.append("|---|---:|")
    lines.append(f"| PTag | {fmt(ptag_rps)} |")
    lines.append(f"| PTagSeries (minimal) | {fmt(series_min_rps)} |")
    lines.append(f"| PTagSeries (complex) | {fmt(series_complex_rps)} |")
    lines.append("")
    lines.append("## Serialization Throughput (records/sec)")
    lines.append("")
    if has_orjson:
        lines.append("| Model | Pydantic JSON | stdlib json | orjson |")
        lines.append("|---|---:|---:|---:|")
        lines.append(f"| PTag | {fmt(ptag_ser_pyd)} | {fmt(ptag_ser_pyd)} | {fmt(ptag_ser_orj)} |")
        # stdlib json equals pydantic’s json.dumps(model_dump()) timing in your script
        lines.append(
            f"| PTagSeries (minimal) | {fmt(series_min_ser_pyd)} | {fmt(series_min_ser_pyd)} | {fmt(series_min_ser_orj)} |"
        )
        lines.append(
            f"| PTagSeries (complex) | {fmt(series_complex_ser_pyd)} | {fmt(series_complex_ser_pyd)} | {fmt(series_complex_ser_orj)} |"
        )
    else:
        lines.append("| Model | Pydantic JSON | stdlib json |")
        lines.append("|---|---:|---:|")
        lines.append(f"| PTag | {fmt(ptag_ser_pyd)} | {fmt(ptag_ser_pyd)} |")
        lines.append(
            f"| PTagSeries (minimal) | {fmt(series_min_ser_pyd)} | {fmt(series_min_ser_pyd)} |"
        )
        lines.append(
            f"| PTagSeries (complex) | {fmt(series_complex_ser_pyd)} | {fmt(series_complex_ser_pyd)} |"
        )
    lines.append("")
    lines.append("## Estimated Memory Usage (bytes per object)")
    lines.append("")
    lines.append("| Model | Bytes/object |")
    lines.append("|---|---:|")
    lines.append(f"| PTag | {fmt(ptag_mem)} |")
    lines.append(f"| PTagSeries (minimal) | {fmt(series_min_mem)} |")
    lines.append(f"| PTagSeries (complex) | {fmt(series_complex_mem)} |")

    out = _repo_root() / "performance_results.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main():
    """Run all benchmarks."""
    print("Civic Transparency PTag Types Performance Benchmark")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"orjson available: {has_orjson}")
    print()

    # Create test data
    minimal_series_data = create_minimal_series()
    complex_series_data = create_complex_series(100)
    provenance_data = create_ptag()

    # Validation benchmarks
    provenance_rps, provenance_obj = benchmark_validation("PTag", PTag, provenance_data, 20000)

    minimal_series_rps, minimal_series_obj = benchmark_validation(
        "PTagSeries (minimal)", PTagSeries, minimal_series_data, 10000
    )

    complex_series_rps, complex_series_obj = benchmark_validation(
        "PTagSeries (100 points)", PTagSeries, complex_series_data, 1000
    )

    # Serialization benchmarks
    provenance_ser = benchmark_serialization("PTag", provenance_obj, 20000)
    minimal_ser = benchmark_serialization("PTagSeries (minimal)", minimal_series_obj, 10000)
    complex_ser = benchmark_serialization("PTagSeries (100 points)", complex_series_obj, 1000)

    # Memory usage
    provenance_mem = measure_memory_usage("PTag", provenance_obj)
    minimal_mem = measure_memory_usage("PTagSeries (minimal)", minimal_series_obj)
    complex_mem = measure_memory_usage("PTagSeries (100 points)", complex_series_obj)

    # Summary
    print("\n" + "=" * 50)
    print(" PERFORMANCE SUMMARY")
    print("=" * 50)

    print("\n  VALIDATION PERFORMANCE")
    print(f"PTag:     {provenance_rps:>8,.0f} records/sec")
    print(f"PTagSeries (minimal):  {minimal_series_rps:>8,.0f} records/sec")
    print(f"PTagSeries (complex):  {complex_series_rps:>8,.0f} records/sec")

    print("\n  SERIALIZATION PERFORMANCE (Pydantic JSON)")
    print(f"PTag:     {provenance_ser['pydantic']:>8,.0f} records/sec")
    print(f"PTagSeries (minimal):  {minimal_ser['pydantic']:>8,.0f} records/sec")
    print(f"PTagSeries (complex):  {complex_ser['pydantic']:>8,.0f} records/sec")

    if has_orjson:
        print("\n  SERIALIZATION PERFORMANCE (orjson)")
        print(f"PTag:     {provenance_ser['orjson']:>8,.0f} records/sec")
        print(f"PTagSeries (minimal):  {minimal_ser['orjson']:>8,.0f} records/sec")
        print(f"PTagSeries (complex):  {complex_ser['orjson']:>8,.0f} records/sec")

    print("\n  MEMORY USAGE")
    print(f"PTag:     {provenance_mem:>8,.0f} bytes")
    print(f"PTagSeries (minimal):  {minimal_mem:>8,.0f} bytes")
    print(f"PTagSeries (complex):  {complex_mem:>8,.0f} bytes")

    _write_text_summary(
        ptag_rps=provenance_rps,
        series_min_rps=minimal_series_rps,
        series_complex_rps=complex_series_rps,
        ptag_ser_pyd=provenance_ser["pydantic"],
        series_min_ser_pyd=minimal_ser["pydantic"],
        series_complex_ser_pyd=complex_ser["pydantic"],
        ptag_ser_orj=provenance_ser.get("orjson"),
        series_min_ser_orj=minimal_ser.get("orjson"),
        series_complex_ser_orj=complex_ser.get("orjson"),
        ptag_mem=provenance_mem,
        series_min_mem=minimal_mem,
        series_complex_mem=complex_mem,
    )

    _write_markdown_summary(
        python_version=sys.version,
        has_orjson=has_orjson,
        ptag_rps=provenance_rps,
        series_min_rps=minimal_series_rps,
        series_complex_rps=complex_series_rps,
        ptag_ser_pyd=provenance_ser["pydantic"],
        series_min_ser_pyd=minimal_ser["pydantic"],
        series_complex_ser_pyd=complex_ser["pydantic"],
        ptag_ser_orj=provenance_ser.get("orjson"),
        series_min_ser_orj=minimal_ser.get("orjson"),
        series_complex_ser_orj=complex_ser.get("orjson"),
        ptag_mem=provenance_mem,
        series_min_mem=minimal_mem,
        series_complex_mem=complex_mem,
    )

    print("\nBenchmark complete!")


if __name__ == "__main__":
    main()
