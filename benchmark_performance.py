#!/usr/bin/env python3
"""
Benchmark script for civic-transparency-types performance.
Run this to get actual performance characteristics for your models.
"""

import json
import time
import sys
import tracemalloc
from datetime import datetime, timezone
from typing import Dict, Any
import statistics
from pydantic import BaseModel

try:
    import orjson

    has_orjson = True
except ImportError:
    has_orjson = False

from ci.transparency.types import Series, ProvenanceTag


def create_minimal_series() -> Dict[str, Any]:
    """Create minimal valid Series data."""
    return {
        "topic": "#BenchmarkTopic",
        "generated_at": "2025-08-19T12:00:00Z",
        "interval": "minute",
        "points": [
            {
                "ts": "2025-08-19T12:00:00Z",
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


def create_complex_series(num_points: int = 100) -> Dict[str, Any]:
    """Create Series data with many points."""
    base_data = create_minimal_series()
    base_point = base_data["points"][0]

    # Generate many time points
    points = []
    for i in range(num_points):
        point = base_point.copy()
        # Vary timestamp
        ts = datetime(2025, 8, 19, 12, i % 60, 0, tzinfo=timezone.utc)
        point["ts"] = ts.isoformat().replace("+00:00", "Z")
        # Vary some values slightly
        point["volume"] = 100 + (i % 50)
        point["reshare_ratio"] = min(1.0, 0.25 + (i % 10) * 0.05)
        points.append(point)

    base_data["points"] = points
    return base_data


def create_provenance_tag() -> Dict[str, Any]:
    """Create minimal valid ProvenanceTag data."""
    return {
        "acct_age_bucket": "1-6m",
        "acct_type": "person",
        "automation_flag": "manual",
        "post_kind": "original",
        "client_family": "mobile",
        "media_provenance": "hash_only",
        "origin_hint": "US-CA",
        "dedup_hash": "a1b2c3d4e5f6789a",
    }


def benchmark_validation(
    name: str,
    model_class: type[BaseModel],
    data: Dict[str, Any],
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

    print(f"  ⏱️  Average time: {avg_time:.4f}s (±{std_time:.4f}s)")
    print(f"  🚀 Records/sec: {records_per_sec:,.0f}")
    print(f"  📏 Time per record: {(avg_time / iterations) * 1000:.3f}ms")

    return records_per_sec, obj


def benchmark_serialization(
    name: str, obj, iterations: int = 10000
) -> dict[str, float]:
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
    print(f"  📋 Pydantic JSON: {results['pydantic']:,.0f} records/sec")

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
    print(f"  🐍 stdlib json: {results['stdlib_json']:,.0f} records/sec")

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
        print(f"  ⚡ orjson: {results['orjson']:,.0f} records/sec")

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
    _: list[type(obj)] = [
        type(obj).model_validate(obj.model_dump()) for _ in range(1000)
    ]

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot2.compare_to(snapshot1, "lineno")
    total_memory = sum(stat.size for stat in top_stats)
    avg_per_object = total_memory / 1000

    print(f"  🔍 sys.getsizeof(): {size:,} bytes")
    print(f"  📊 Estimated per object: {avg_per_object:,.0f} bytes")
    print(f"  📦 JSON size: {len(obj.model_dump_json()):,} bytes")

    return avg_per_object


def main():
    """Run all benchmarks."""
    print("🎯 Civic Transparency Types Performance Benchmark")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"orjson available: {has_orjson}")
    print()

    # Create test data
    minimal_series_data = create_minimal_series()
    complex_series_data = create_complex_series(100)
    provenance_data = create_provenance_tag()

    # Validation benchmarks
    provenance_rps, provenance_obj = benchmark_validation(
        "ProvenanceTag", ProvenanceTag, provenance_data, 20000
    )

    minimal_series_rps, minimal_series_obj = benchmark_validation(
        "Series (minimal)", Series, minimal_series_data, 10000
    )

    complex_series_rps, complex_series_obj = benchmark_validation(
        "Series (100 points)", Series, complex_series_data, 1000
    )

    # Serialization benchmarks
    provenance_ser = benchmark_serialization("ProvenanceTag", provenance_obj, 20000)
    minimal_ser = benchmark_serialization("Series (minimal)", minimal_series_obj, 10000)
    complex_ser = benchmark_serialization(
        "Series (100 points)", complex_series_obj, 1000
    )

    # Memory usage
    provenance_mem = measure_memory_usage("ProvenanceTag", provenance_obj)
    minimal_mem = measure_memory_usage("Series (minimal)", minimal_series_obj)
    complex_mem = measure_memory_usage("Series (100 points)", complex_series_obj)

    # Summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)

    print("\n🔬 VALIDATION PERFORMANCE")
    print(f"ProvenanceTag:     {provenance_rps:>8,.0f} records/sec")
    print(f"Series (minimal):  {minimal_series_rps:>8,.0f} records/sec")
    print(f"Series (complex):  {complex_series_rps:>8,.0f} records/sec")

    print("\n📤 SERIALIZATION PERFORMANCE (Pydantic JSON)")
    print(f"ProvenanceTag:     {provenance_ser['pydantic']:>8,.0f} records/sec")
    print(f"Series (minimal):  {minimal_ser['pydantic']:>8,.0f} records/sec")
    print(f"Series (complex):  {complex_ser['pydantic']:>8,.0f} records/sec")

    if has_orjson:
        print("\n⚡ SERIALIZATION PERFORMANCE (orjson)")
        print(f"ProvenanceTag:     {provenance_ser['orjson']:>8,.0f} records/sec")
        print(f"Series (minimal):  {minimal_ser['orjson']:>8,.0f} records/sec")
        print(f"Series (complex):  {complex_ser['orjson']:>8,.0f} records/sec")

    print("\n💾 MEMORY USAGE")
    print(f"ProvenanceTag:     {provenance_mem:>8,.0f} bytes")
    print(f"Series (minimal):  {minimal_mem:>8,.0f} bytes")
    print(f"Series (complex):  {complex_mem:>8,.0f} bytes")

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
