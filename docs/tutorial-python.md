# Python SDK Tutorial

Complete guide to using the FakePhoto.ai Python SDK for AI-generated content detection.

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Configuration](#configuration)
4. [Analyzing Images](#analyzing-images)
5. [Analyzing Videos](#analyzing-videos)
6. [Batch Processing](#batch-processing)
7. [Advanced Features](#advanced-features)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Installation

```bash
pip install fakephoto-ai
```

With optional dependencies:

```bash
# Development tools
pip install fakephoto-ai[dev]

# All extras
pip install fakephoto-ai[all]
```

---

## Basic Usage

### Quick Start

```python
from fakephoto import analyze_image

result = analyze_image(
    "photo.jpg",
    openai_key="sk-your-key"
)

print(f"AI Generated: {result.is_ai_generated}")
print(f"Confidence: {result.confidence_score}%")
```

### Using the Detector Class

For more control, use the `MultiModelDetector` class:

```python
from fakephoto import MultiModelDetector

detector = MultiModelDetector(
    openai_api_key="sk-openai-key",
    google_api_key="google-key",
    anthropic_api_key="sk-ant-key",
    confidence_threshold=0.7
)

result = detector.analyze("photo.jpg")
```

---

## Configuration

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

Load them in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

detector = MultiModelDetector(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `openai_api_key` | str | None | OpenAI API key |
| `google_api_key` | str | None | Google API key |
| `anthropic_api_key` | str | None | Anthropic API key |
| `confidence_threshold` | float | 0.7 | Threshold for AI detection (0.0-1.0) |

---

## Analyzing Images

### Single Image Analysis

```python
result = detector.analyze("path/to/image.jpg")

# Access results
print(f"Filename: {result.filename}")
print(f"AI Generated: {result.is_ai_generated}")
print(f"Confidence Score: {result.confidence_score}")  # 0-100
print(f"Consensus: {result.consensus}")  # strong, moderate, weak
```

### Understanding the Result

```python
# Model-specific results
for model_name, scores in result.model_scores.items():
    print(f"{model_name}:")
    print(f"  AI Probability: {scores['ai_probability']}")
    print(f"  Confidence: {scores['confidence']}")

# Detected indicators
print("\nIndicators:")
for indicator in result.indicators:
    print(f"  - {indicator}")

# Recommendations
print("\nRecommendations:")
for rec in result.recommendations:
    print(f"  - {rec}")
```

### Supported Image Formats

- JPG/JPEG
- PNG
- WebP
- HEIC

---

## Analyzing Videos

The SDK automatically extracts frames from videos for analysis:

```python
result = detector.analyze("path/to/video.mp4")

print(f"Video: {result.filename}")
print(f"AI Generated: {result.is_ai_generated}")
```

### Supported Video Formats

- MP4
- AVI
- MOV
- MKV
- WebM

---

## Batch Processing

### Process a Folder

```python
results = detector.analyze_batch("/path/to/folder")

for result in results:
    print(f"{result.filename}: {result.confidence_score}% AI probability")
```

### Filtering Results

```python
results = detector.analyze_batch("/path/to/folder")

# Find high-confidence AI-generated content
ai_content = [
    r for r in results 
    if r.is_ai_generated and r.confidence_score > 80
]

print(f"Found {len(ai_content)} likely AI-generated files")
```

### Progress Tracking

```python
import os

folder = "/path/to/images"
files = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]

results = []
for i, filename in enumerate(files, 1):
    print(f"Processing {i}/{len(files)}: {filename}")
    try:
        result = detector.analyze(os.path.join(folder, filename))
        results.append(result)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
```

---

## Advanced Features

### Custom Confidence Thresholds

```python
# Stricter detection
detector = MultiModelDetector(
    openai_api_key="sk-key",
    confidence_threshold=0.85  # 85% threshold
)

# More lenient
detector = MultiModelDetector(
    openai_api_key="sk-key",
    confidence_threshold=0.5   # 50% threshold
)
```

### Model Selection

Use specific models only:

```python
# OpenAI only
detector = MultiModelDetector(openai_api_key="sk-key")

# Google only
detector = MultiModelDetector(google_api_key="key")

# Anthropic only
detector = MultiModelDetector(anthropic_api_key="sk-key")
```

### Async Support (Coming Soon)

```python
import asyncio
from fakephoto import AsyncMultiModelDetector

async def analyze_multiple():
    detector = AsyncMultiModelDetector(
        openai_api_key="sk-key",
        google_api_key="key"
    )
    
    results = await asyncio.gather(
        detector.analyze("image1.jpg"),
        detector.analyze("image2.jpg"),
        detector.analyze("image3.jpg")
    )
    
    return results

results = asyncio.run(analyze_multiple())
```

---

## Error Handling

### Common Exceptions

```python
from fakephoto import MultiModelDetector
from fakephoto.exceptions import (
    FileNotFoundError,
    UnsupportedFormatError,
    APIError,
    RateLimitError
)

detector = MultiModelDetector(openai_api_key="sk-key")

try:
    result = detector.analyze("image.jpg")
except FileNotFoundError:
    print("File not found - check the path")
except UnsupportedFormatError:
    print("File format not supported")
except RateLimitError:
    print("Rate limit hit - wait before retrying")
except APIError as e:
    print(f"API error: {e}")
```

### Graceful Degradation

```python
def safe_analyze(detector, filepath):
    """Analyze with fallback handling"""
    try:
        return detector.analyze(filepath)
    except Exception as e:
        print(f"Analysis failed for {filepath}: {e}")
        return None

# Process folder with errors handled
results = []
for file in os.listdir("images"):
    result = safe_analyze(detector, os.path.join("images", file))
    if result:
        results.append(result)
```

---

## Best Practices

### 1. Use Multiple Models

```python
# Best accuracy - use all three models
detector = MultiModelDetector(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### 2. Implement Caching

```python
import json
import hashlib
from pathlib import Path

def get_cache_key(filepath):
    """Generate cache key from file content"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def analyze_with_cache(detector, filepath, cache_dir=".cache"):
    """Analyze with file-based caching"""
    Path(cache_dir).mkdir(exist_ok=True)
    
    cache_key = get_cache_key(filepath)
    cache_file = Path(cache_dir) / f"{cache_key}.json"
    
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    
    result = detector.analyze(filepath)
    
    with open(cache_file, 'w') as f:
        json.dump(result.__dict__, f)
    
    return result
```

### 3. Batch Processing with Progress

```python
from tqdm import tqdm

folder = "images"
files = list(Path(folder).glob("*.jpg"))

results = []
for file in tqdm(files, desc="Analyzing images"):
    result = detector.analyze(file)
    results.append(result)
```

### 4. Export Results

```python
import csv
import json

# Export to JSON
with open("results.json", "w") as f:
    json.dump([r.__dict__ for r in results], f, indent=2)

# Export to CSV
with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "is_ai_generated", "confidence_score"])
    for r in results:
        writer.writerow([r.filename, r.is_ai_generated, r.confidence_score])
```

---

## Complete Example

```python
"""
Complete example: Analyze a folder and generate a report
"""
import os
from pathlib import Path
from fakephoto import MultiModelDetector
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize detector
    detector = MultiModelDetector(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        confidence_threshold=0.7
    )
    
    # Analyze folder
    folder = input("Enter folder path: ")
    print(f"\nAnalyzing images in: {folder}\n")
    
    results = detector.analyze_batch(folder)
    
    # Generate report
    total = len(results)
    ai_generated = sum(1 for r in results if r.is_ai_generated)
    high_confidence = sum(1 for r in results if r.confidence_score > 90)
    
    print("=" * 50)
    print("ANALYSIS REPORT")
    print("=" * 50)
    print(f"Total files analyzed: {total}")
    print(f"AI-generated detected: {ai_generated} ({100*ai_generated/total:.1f}%)")
    print(f"High confidence (>90%): {high_confidence}")
    print("\nDetailed Results:")
    print("-" * 50)
    
    for r in sorted(results, key=lambda x: x.confidence_score, reverse=True):
        status = "🤖 AI" if r.is_ai_generated else "✅ Authentic"
        print(f"{status} | {r.confidence_score:5.1f}% | {r.filename}")

if __name__ == "__main__":
    main()
```

---

## Next Steps

- [REST API Tutorial](tutorial-api.md) - Integrate with your backend
- [Batch Processing Guide](tutorial-batch.md) - Large-scale processing
- [Example: Journalist Workflow](../examples/journalist-workflow.md)
