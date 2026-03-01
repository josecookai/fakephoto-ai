# Batch Processing Guide

Process thousands of images and videos efficiently with FakePhoto.ai's batch processing capabilities.

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use Batch Processing](#when-to-use-batch-processing)
3. [Python SDK Batch Processing](#python-sdk-batch-processing)
4. [REST API Batch Processing](#rest-api-batch-processing)
5. [Advanced Patterns](#advanced-patterns)
6. [Monitoring Progress](#monitoring-progress)
7. [Optimization Tips](#optimization-tips)
8. [Error Handling at Scale](#error-handling-at-scale)

---

## Overview

Batch processing allows you to:
- Analyze thousands of files in a single operation
- Process files asynchronously
- Receive progress updates via webhooks
- Resume interrupted jobs

---

## When to Use Batch Processing

| Use Case | Recommended Approach |
|----------|---------------------|
| 1-10 files | Individual API calls |
| 10-100 files | Batch API with polling |
| 100+ files | Batch API with webhooks |
| Real-time needs | Individual API calls |
| Scheduled processing | Batch API with cron |

---

## Python SDK Batch Processing

### Basic Batch Analysis

```python
from fakephoto import MultiModelDetector
import os

# Initialize detector
detector = MultiModelDetector(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Analyze entire folder
results = detector.analyze_batch("/path/to/images")

# Process results
for result in results:
    status = "AI" if result.is_ai_generated else "Authentic"
    print(f"{result.filename}: {status} ({result.confidence_score:.1f}%)")
```

### Filtering Before Processing

```python
from pathlib import Path

# Define supported formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4', '.mov'}

def get_files_to_process(folder):
    """Get only supported files"""
    folder = Path(folder)
    return [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
    ]

files = get_files_to_process("/path/to/images")
print(f"Found {len(files)} files to analyze")
```

### Chunked Processing

For very large batches, process in chunks:

```python
def process_in_chunks(detector, files, chunk_size=50):
    """Process files in smaller chunks"""
    results = []
    
    for i in range(0, len(files), chunk_size):
        chunk = files[i:i + chunk_size]
        print(f"Processing chunk {i//chunk_size + 1}/{(len(files)-1)//chunk_size + 1}")
        
        for file in chunk:
            try:
                result = detector.analyze(file)
                results.append(result)
            except Exception as e:
                print(f"Error with {file}: {e}")
    
    return results

# Usage
from pathlib import Path
files = list(Path("images").glob("*.jpg"))
results = process_in_chunks(detector, files, chunk_size=50)
```

---

## REST API Batch Processing

### Submitting a Batch Job

```bash
# Submit multiple files
curl -X POST https://api.fakephoto.ai/v1/batch \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "files=@image3.jpg" \
  -F "webhook_url=https://your-app.com/webhook"
```

### Python Implementation

```python
import requests
import os
from pathlib import Path

API_KEY = os.getenv("FAKEPHOTO_API_KEY")
BASE_URL = "https://api.fakephoto.ai/v1"

def submit_batch(folder_path, webhook_url=None):
    """Submit batch job for all files in folder"""
    url = f"{BASE_URL}/batch"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    # Prepare files
    files = []
    folder = Path(folder_path)
    for filepath in folder.iterdir():
        if filepath.is_file():
            files.append(
                ("files", (filepath.name, open(filepath, "rb")))
            )
    
    data = {}
    if webhook_url:
        data["webhook_url"] = webhook_url
    
    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()
    
    return response.json()

# Submit batch
batch = submit_batch("/path/to/images", webhook_url="https://your-app.com/webhook")
print(f"Batch ID: {batch['batch_id']}")
print(f"Total files: {batch['total_files']}")
```

### Checking Batch Status

```python
def check_batch_status(batch_id):
    """Check status of batch job"""
    url = f"{BASE_URL}/batch/{batch_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Poll until complete
import time

batch_id = batch['batch_id']
while True:
    status = check_batch_status(batch_id)
    
    progress = status['progress']
    print(f"Progress: {progress['completed']}/{progress['total']} completed")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)  # Wait 5 seconds between checks

print("Batch processing complete!")
```

---

## Advanced Patterns

### Parallel Processing with Threading

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from fakephoto import MultiModelDetector

def analyze_file(detector, filepath):
    """Analyze a single file with error handling"""
    try:
        result = detector.analyze(filepath)
        return {"file": filepath, "result": result, "error": None}
    except Exception as e:
        return {"file": filepath, "result": None, "error": str(e)}

def parallel_batch_process(detector, files, max_workers=5):
    """Process files in parallel"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(analyze_file, detector, f): f 
            for f in files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)
            
            # Progress update
            completed = len(results)
            total = len(files)
            print(f"Progress: {completed}/{total} ({100*completed/total:.1f}%)")
    
    return results

# Usage
from pathlib import Path
detector = MultiModelDetector(openai_api_key="sk-key")
files = list(Path("images").glob("*.jpg"))

results = parallel_batch_process(detector, files, max_workers=5)

# Separate successful and failed
successful = [r for r in results if r["error"] is None]
failed = [r for r in results if r["error"] is not None]

print(f"Successful: {len(successful)}, Failed: {len(failed)}")
```

### Async Processing with asyncio

```python
import asyncio
import aiohttp
import aiofiles

async def analyze_file_async(session, api_key, filepath):
    """Async file analysis"""
    url = "https://api.fakephoto.ai/v1/analyze"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with aiofiles.open(filepath, "rb") as f:
        file_content = await f.read()
        
    data = aiohttp.FormData()
    data.add_field("file", file_content, filename=filepath.name)
    
    async with session.post(url, headers=headers, data=data) as resp:
        return await resp.json()

async def batch_process_async(files, api_key, max_concurrent=10):
    """Process files with concurrency limit"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(session, filepath):
        async with semaphore:
            return await analyze_file_async(session, api_key, filepath)
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_with_limit(session, f) for f in files]
        results = []
        
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            print(f"Completed: {len(results)}/{len(files)}")
        
        return results

# Usage
from pathlib import Path
files = list(Path("images").glob("*.jpg"))
results = asyncio.run(batch_process_async(files, "api-key", max_concurrent=5))
```

---

## Monitoring Progress

### Progress Bar with tqdm

```python
from tqdm import tqdm

def process_with_progress(detector, files):
    """Process files with progress bar"""
    results = []
    
    with tqdm(total=len(files), desc="Analyzing") as pbar:
        for filepath in files:
            try:
                result = detector.analyze(filepath)
                results.append(result)
                
                # Update progress description
                ai_count = sum(1 for r in results if r.is_ai_generated)
                pbar.set_postfix({
                    "AI": ai_count,
                    "Authentic": len(results) - ai_count
                })
            except Exception as e:
                print(f"\nError with {filepath}: {e}")
            
            pbar.update(1)
    
    return results
```

### JSONL Logging

```python
import json
from datetime import datetime

def log_result(result, log_file="batch_results.jsonl"):
    """Append result to JSONL file"""
    with open(log_file, "a") as f:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "filename": result.filename,
            "is_ai_generated": result.is_ai_generated,
            "confidence_score": result.confidence_score
        }
        f.write(json.dumps(log_entry) + "\n")

# Use during processing
for file in files:
    result = detector.analyze(file)
    log_result(result)
```

---

## Optimization Tips

### 1. Pre-filter Files

```python
import os

def should_process_file(filepath):
    """Check if file should be processed"""
    # Skip already processed
    cache_file = f"{filepath}.analyzed"
    if os.path.exists(cache_file):
        return False
    
    # Skip files too small (likely corrupted)
    if os.path.getsize(filepath) < 1024:  # 1KB
        return False
    
    # Skip files too large (>100MB)
    if os.path.getsize(filepath) > 100 * 1024 * 1024:
        return False
    
    return True

files = [f for f in all_files if should_process_file(f)]
```

### 2. Implement Caching

```python
import hashlib
import json
from pathlib import Path

def get_file_hash(filepath):
    """Get MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def cached_analyze(detector, filepath, cache_dir=".cache"):
    """Analyze with caching"""
    Path(cache_dir).mkdir(exist_ok=True)
    
    file_hash = get_file_hash(filepath)
    cache_file = Path(cache_dir) / f"{file_hash}.json"
    
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    
    result = detector.analyze(filepath)
    
    with open(cache_file, "w") as f:
        json.dump(result.__dict__, f, default=str)
    
    return result
```

### 3. Prioritize High-Risk Content

```python
def prioritize_files(files):
    """Prioritize files for processing"""
    # Example: Process suspicious files first
    priority = {
        "suspicious": [],
        "normal": []
    }
    
    for file in files:
        # Simple heuristic: check filename patterns
        name = file.name.lower()
        if any(term in name for term in ["ai", "generated", "deepfake", "fake"]):
            priority["suspicious"].append(file)
        else:
            priority["normal"].append(file)
    
    return priority["suspicious"] + priority["normal"]
```

---

## Error Handling at Scale

### Exponential Backoff

```python
import time
import random

def analyze_with_backoff(detector, filepath, max_retries=5):
    """Analyze with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return detector.analyze(filepath)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Retry {attempt + 1} after {wait:.1f}s: {e}")
            time.sleep(wait)
```

### Dead Letter Queue

```python
import json
from pathlib import Path

def process_with_dlq(detector, files, dlq_file="failed_files.json"):
    """Process with dead letter queue for failures"""
    failed = []
    successful = []
    
    for filepath in files:
        try:
            result = detector.analyze(filepath)
            successful.append({"file": str(filepath), "result": result})
        except Exception as e:
            print(f"Failed: {filepath}")
            failed.append({
                "file": str(filepath),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    # Save failed files for later retry
    if failed:
        with open(dlq_file, "w") as f:
            json.dump(failed, f, indent=2)
        print(f"Saved {len(failed)} failed files to {dlq_file}")
    
    return successful, failed
```

---

## Complete Example

```python
"""
Complete batch processing example with all best practices
"""
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from fakephoto import MultiModelDetector
from tqdm import tqdm

class BatchProcessor:
    def __init__(self, api_keys, cache_dir=".cache"):
        self.detector = MultiModelDetector(**api_keys)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.results = []
        self.failed = []
    
    def get_cache_path(self, filepath):
        """Get cache path for file"""
        import hashlib
        file_hash = hashlib.md5(open(filepath, "rb").read()).hexdigest()
        return self.cache_dir / f"{file_hash}.json"
    
    def process_file(self, filepath):
        """Process single file with caching"""
        cache_path = self.get_cache_path(filepath)
        
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)
        
        result = self.detector.analyze(filepath)
        
        with open(cache_path, "w") as f:
            json.dump(result.__dict__, f, default=str)
        
        return result
    
    def process_folder(self, folder, output_file="results.json"):
        """Process entire folder"""
        folder = Path(folder)
        files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}
        ]
        
        print(f"Found {len(files)} files to process")
        
        for filepath in tqdm(files, desc="Analyzing"):
            try:
                result = self.process_file(filepath)
                self.results.append({
                    "file": str(filepath),
                    "result": result.__dict__ if hasattr(result, '__dict__') else result
                })
            except Exception as e:
                self.failed.append({"file": str(filepath), "error": str(e)})
        
        # Save results
        output = {
            "processed_at": datetime.utcnow().isoformat(),
            "total_files": len(files),
            "successful": len(self.results),
            "failed": len(self.failed),
            "results": self.results,
            "failed_files": self.failed
        }
        
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {output_file}")
        print(f"Successful: {len(self.results)}, Failed: {len(self.failed)}")
        
        # Summary
        ai_count = sum(1 for r in self.results 
                      if r["result"].get("is_ai_generated", False))
        print(f"AI-generated detected: {ai_count} ({100*ai_count/len(self.results):.1f}%)")
        
        return output

# Usage
if __name__ == "__main__":
    processor = BatchProcessor({
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "google_api_key": os.getenv("GOOGLE_API_KEY")
    })
    
    processor.process_folder("/path/to/images")
```

---

## Next Steps

- [Python SDK Tutorial](tutorial-python.md)
- [REST API Tutorial](tutorial-api.md)
- [API Reference](API.md)
