# REST API Tutorial

Complete guide to integrating FakePhoto.ai's REST API into your applications.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Your First Request](#your-first-request)
4. [Analyzing Images](#analyzing-images)
5. [Analyzing Videos](#analyzing-videos)
6. [Batch Processing](#batch-processing)
7. [Webhooks](#webhooks)
8. [Error Handling](#error-handling)
9. [Language Examples](#language-examples)

---

## Getting Started

### Base URL

```
https://api.fakephoto.ai/v1
```

### API Keys

Sign up at [fakephoto.ai](https://fakephoto.ai) to get your API key.

---

## Authentication

Include your API key in the Authorization header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Testing Your Key

```bash
curl https://api.fakephoto.ai/v1/health \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Your First Request

### Analyze an Image

```bash
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/image.jpg"
```

### Understanding the Response

```json
{
  "id": "anal_1234567890",
  "status": "completed",
  "filename": "image.jpg",
  "result": {
    "is_ai_generated": true,
    "confidence_score": 87.5,
    "consensus": "strong"
  }
}
```

| Field | Description |
|-------|-------------|
| `is_ai_generated` | Boolean indicating AI-generated content |
| `confidence_score` | 0-100 confidence percentage |
| `consensus` | Model agreement level: `strong`, `moderate`, `weak` |

---

## Analyzing Images

### Upload from File

```bash
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@photo.jpg" \
  -F "models=[\"openai\",\"gemini\"]"
```

### Analyze by URL

```bash
curl -X POST https://api.fakephoto.ai/v1/analyze-url \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/image.jpg",
    "models": ["openai", "gemini", "anthropic"]
  }'
```

### Request Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | File | Image file (multipart/form-data) |
| `url` | String | Public URL to image |
| `models` | Array | Models to use: `openai`, `gemini`, `anthropic` |
| `webhook_url` | String | URL for result notification |
| `priority` | String | `low`, `normal`, `high` |

---

## Analyzing Videos

Videos are processed by extracting and analyzing frames:

```bash
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@video.mp4"
```

### Video Response

```json
{
  "id": "anal_vid_1234567890",
  "status": "completed",
  "filename": "video.mp4",
  "content_type": "video/mp4",
  "result": {
    "is_ai_generated": false,
    "confidence_score": 23.5,
    "frames_analyzed": 5,
    "frame_results": [
      {"timestamp": 0.0, "ai_probability": 0.15},
      {"timestamp": 2.5, "ai_probability": 0.22},
      {"timestamp": 5.0, "ai_probability": 0.18}
    ]
  }
}
```

---

## Batch Processing

### Submit Batch Job

```bash
curl -X POST https://api.fakephoto.ai/v1/batch \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "files=@image3.jpg"
```

### Check Batch Status

```bash
curl https://api.fakephoto.ai/v1/batch/BATCH_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Batch Response

```json
{
  "batch_id": "batch_1234567890",
  "status": "completed",
  "progress": {
    "total": 3,
    "completed": 3,
    "failed": 0
  },
  "results": [
    {
      "file_id": "file_abc123",
      "filename": "image1.jpg",
      "status": "completed",
      "result": { /* analysis result */ }
    }
  ]
}
```

---

## Webhooks

Receive real-time notifications instead of polling.

### Setting Up Webhooks

```bash
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@image.jpg" \
  -F "webhook_url=https://your-app.com/webhook"
```

### Webhook Payload

```json
{
  "event": "analysis.completed",
  "timestamp": "2024-01-15T10:30:05Z",
  "data": {
    "analysis_id": "anal_1234567890",
    "status": "completed",
    "result": {
      "is_ai_generated": true,
      "confidence_score": 87.5
    }
  }
}
```

### Webhook Security

Verify webhook authenticity:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

# Usage
signature = request.headers['X-Webhook-Signature']
if verify_webhook(request.body, signature, WEBHOOK_SECRET):
    # Process webhook
    pass
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "invalid_file_format",
    "message": "The provided file format is not supported.",
    "request_id": "req_1234567890"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Invalid API key |
| `rate_limit_exceeded` | 429 | Too many requests |
| `invalid_file_format` | 400 | Unsupported file type |
| `file_too_large` | 413 | File > 100MB |

### Retry Logic

```python
import time
import requests

def analyze_with_retry(filepath, max_retries=3):
    url = "https://api.fakephoto.ai/v1/analyze"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    
    for attempt in range(max_retries):
        try:
            with open(filepath, 'rb') as f:
                response = requests.post(
                    url,
                    headers=headers,
                    files={"file": f}
                )
            
            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 429:
                # Rate limit - wait and retry
                time.sleep(2 ** attempt)
                continue
                
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

---

## Language Examples

### Python

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "https://api.fakephoto.ai/v1"

def analyze_image(filepath):
    url = f"{BASE_URL}/analyze"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    with open(filepath, 'rb') as f:
        files = {"file": f}
        response = requests.post(url, headers=headers, files=files)
    
    response.raise_for_status()
    return response.json()

# Usage
result = analyze_image("photo.jpg")
print(f"AI Generated: {result['result']['is_ai_generated']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_KEY = 'your-api-key';
const BASE_URL = 'https://api.fakephoto.ai/v1';

async function analyzeImage(filepath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filepath));
    
    const response = await axios.post(
        `${BASE_URL}/analyze`,
        form,
        {
            headers: {
                ...form.getHeaders(),
                'Authorization': `Bearer ${API_KEY}`
            }
        }
    );
    
    return response.data;
}

// Usage
analyzeImage('photo.jpg')
    .then(result => console.log(result))
    .catch(err => console.error(err));
```

### cURL

```bash
# Simple analysis
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@image.jpg"

# With webhook
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@image.jpg" \
  -F "webhook_url=https://your-app.com/webhook"
```

### Go

```go
package main

import (
    "bytes"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func analyzeImage(filepath string) (*http.Response, error) {
    file, err := os.Open(filepath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)
    part, _ := writer.CreateFormFile("file", filepath)
    io.Copy(part, file)
    writer.Close()
    
    req, _ := http.NewRequest("POST", "https://api.fakephoto.ai/v1/analyze", body)
    req.Header.Add("Authorization", "Bearer YOUR_API_KEY")
    req.Header.Add("Content-Type", writer.FormDataContentType())
    
    client := &http.Client{}
    return client.Do(req)
}
```

---

## Rate Limits

| Tier | Requests/Min | Requests/Hour |
|------|-------------|---------------|
| Free | 10 | 100 |
| Pro | 60 | 2,000 |
| Enterprise | 300 | 10,000 |

Check rate limits in response headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

---

## SDKs

### Official SDKs

- **Python:** `pip install fakephoto-ai`
- **Node.js:** `npm install @fakephoto/api`
- **Go:** `go get github.com/fakephoto/go-sdk`

### Using Python SDK

```python
from fakephoto import MultiModelDetector

detector = MultiModelDetector(openai_api_key="sk-key")
result = detector.analyze("image.jpg")
```

---

## Next Steps

- [Full API Reference](API.md)
- [Batch Processing Guide](tutorial-batch.md)
- [Python SDK Tutorial](tutorial-python.md)
