# Performance Guide

When working with civic transparency data at scale, these performance characteristics and optimizations can help you build efficient applications.

## Benchmark Results

Performance measured on **Windows Python 3.11.9** (your results may vary based on hardware and Python version):

### Validation Performance

| Model Type | Records/sec | Time per Record | Use Case |
|------------|-------------|-----------------|----------|
| **ProvenanceTag** | ~160,000 | 0.006ms | Post metadata validation |
| **Series (minimal)** | ~25,000 | 0.040ms | Simple time series |
| **Series (100 points)** | ~259 | 3.861ms | Complex time series |

### JSON Serialization Performance

| Model Type | Pydantic JSON | stdlib json | Speedup |
|------------|---------------|-------------|---------|
| **ProvenanceTag** | ~651,000/sec | ~269,000/sec | 2.4x |
| **Series (minimal)** | ~228,000/sec | ~91,000/sec | 2.5x |
| **Series (100 points)** | ~3,531/sec | ~1,511/sec | 2.3x |

**Key Insight:** Pydantic's `model_dump_json()` is consistently ~2.4x faster than `model_dump()` + `json.dumps()`.

### Memory Usage

| Model Type | Memory per Object | JSON Size | Efficiency |
|------------|------------------|-----------|------------|
| **ProvenanceTag** | ~1,084 bytes | 207 bytes | 5.2x overhead |
| **Series (minimal)** | ~7,127 bytes | 502 bytes | 14.2x overhead |
| **Series (100 points)** | ~660,159 bytes | 40,796 bytes | 16.2x overhead |

**Memory overhead** includes Python object structures, Pydantic metadata, and validation caching.

## Performance Patterns

### 1. Complexity Scaling
- **ProvenanceTag**: Simple enum validation is very fast
- **Series**: Scales linearly with number of data points
- **Nested validation**: Each point requires full coordinate validation

### 2. Serialization vs Validation
- **Serialization is faster**: JSON generation is 4-25x faster than validation
- **Pydantic optimized**: Built-in JSON serializer beats stdlib significantly
- **Memory efficient**: JSON representation is much more compact

### 3. Privacy-Preserving Design Impact
The privacy-by-design approach actually **helps performance**:
- **Bucketed enums** (like `acct_age_bucket`) validate faster than ranges
- **Categorical data** requires less processing than continuous values
- **Aggregated structures** reduce individual record complexity

## Optimization Strategies

### High-Throughput Validation

For processing large volumes of civic data:

```python
from ci.transparency.types import ProvenanceTag
from typing import List, Dict, Any
import logging

def process_provenance_batch(data_list: List[Dict[str, Any]]) -> List[ProvenanceTag]:
    """Process ~160K records/second efficiently."""
    results = []
    errors = 0
    
    for data in data_list:
        try:
            tag = ProvenanceTag.model_validate(data)
            results.append(tag)
        except ValidationError as e:
            errors += 1
            if errors < 10:  # Log first few errors
                logging.warning(f"Validation failed: {e}")
    
    return results

# Expected throughput: ~160,000 ProvenanceTags/second
```

### Efficient Series Processing

For time series data with many points:

```python
from ci.transparency.types import Series

def process_series_stream(data_stream):
    """Stream processing for memory efficiency."""
    for series_data in data_stream:
        # Validate once per series (~259/second for 100-point series)
        series = Series.model_validate(series_data)
        
        # Process and immediately serialize to save memory
        result = series.model_dump_json()  # ~3,531/second
        yield result
        
        # series goes out of scope, freeing ~660KB
```

### JSON Optimization

Choose serialization method based on your needs:

```python
# Fastest: Use Pydantic's built-in JSON (recommended)
json_str = series.model_dump_json()  # ~228K/sec for minimal series

# Alternative: For custom JSON formatting
import orjson  # Install separately for even better performance

data = series.model_dump(mode='json')  # Convert enums to values
json_bytes = orjson.dumps(data)       # Potentially faster than stdlib
```

### Memory Management

For processing large datasets:

```python
import gc
from typing import Iterator

def memory_efficient_processing(large_dataset: Iterator[dict]):
    """Process data without loading everything into memory."""
    batch_size = 1000
    batch = []
    
    for record in large_dataset:
        batch.append(record)
        
        if len(batch) >= batch_size:
            # Process batch
            results = [ProvenanceTag.model_validate(data) for data in batch]
            
            # Yield results and clear memory
            yield from results
            batch.clear()
            
            # Optional: Force garbage collection for long-running processes
            if len(results) % 10000 == 0:
                gc.collect()
```

## Production Considerations

### Database Integration

Based on the memory usage, consider your storage strategy:

```python
# For ProvenanceTag (1KB each): Can safely keep thousands in memory
provenance_cache = {}  # OK to cache frequently accessed tags

# For Series (7KB-660KB each): Stream processing recommended
def store_series_efficiently(series: Series):
    # Store as compressed JSON rather than keeping objects in memory
    json_data = series.model_dump_json()
    compressed = gzip.compress(json_data.encode())
    database.store(compressed)
```

### API Design

Design your APIs based on these performance characteristics:

```python
from fastapi import FastAPI
from ci.transparency.types import ProvenanceTag, Series

app = FastAPI()

@app.post("/provenance/batch")
async def upload_provenance_batch(tags: List[ProvenanceTag]):
    # Can handle large batches efficiently (~160K/sec validation)
    return {"processed": len(tags)}

@app.post("/series")
async def upload_series(series: Series):
    # Individual series upload (validation cost depends on point count)
    point_count = len(series.points)
    if point_count > 1000:
        # Consider async processing for very large series
        return {"status": "queued", "points": point_count}
    return {"status": "processed", "points": point_count}
```

## When Performance Matters

### High-Performance Scenarios
- **Real-time civic monitoring**: ProvenanceTag validation at 160K/sec supports live analysis
- **Batch processing**: Can process millions of records efficiently
- **API endpoints**: Fast enough for responsive web applications

### Optimization Not Needed
- **Typical civic research**: These speeds far exceed most analytical workloads
- **Small datasets**: Optimization overhead not worth it for <10K records
- **Prototype development**: Focus on correctness first, optimize later

## Monitoring Performance

Add performance monitoring to your applications:

```python
import time
import logging

class PerformanceMonitor:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, *args):
        duration = time.perf_counter() - self.start_time
        logging.info(f"{self.name} took {duration:.3f}s")

# Usage
with PerformanceMonitor("ProvenanceTag validation"):
    tags = [ProvenanceTag.model_validate(data) for data in batch]
```

## Summary

The civic transparency types deliver **high performance** for privacy-preserving data processing:

- **Production-ready speeds**: 160K+ validations/second for metadata
- **Efficient serialization**: Built-in JSON optimization  
- **Predictable scaling**: Performance scales with data complexity
- **Memory conscious**: Reasonable overhead for rich validation

The privacy-by-design architecture (bucketed enums, aggregated data) **improves performance** compared to handling raw, detailed data structures.
