# FakePhoto.ai API Documentation

## Overview

The FakePhoto.ai REST API provides programmatic access to our multi-model AI detection engine. Verify if images and videos are AI-generated using OpenAI GPT-4V, Google Gemini, and Anthropic Claude.

**Base URL:** `https://api.fakephoto.ai/v1`

**API Version:** 1.0.0

---

## Authentication

All API requests require authentication using an API key. Include your API key in the `Authorization` header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Obtaining an API Key

1. Sign up at [https://fakephoto.ai](https://fakephoto.ai)
2. Navigate to **Settings > API Keys**
3. Generate a new API key
4. Store it securely - it won't be shown again

### API Key Permissions

| Permission | Description |
|------------|-------------|
| `analyze:read` | Analyze images and videos |
| `batch:read` | Submit batch processing jobs |
| `jobs:read` | View job status and results |

---

## Rate Limits

Rate limits are applied based on your subscription tier:

| Tier | Requests/Min | Requests/Hour | Batch Jobs/Day |
|------|-------------|---------------|----------------|
| Free | 10 | 100 | 5 |
| Pro | 60 | 2,000 | 100 |
| Enterprise | 300 | 10,000 | Unlimited |

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Please retry after 60 seconds.",
  "retry_after": 60
}
```

**Best Practices:**
- Implement exponential backoff for retries
- Cache results when possible
- Use batch endpoints for multiple files

---

## Endpoints

### 1. Analyze Image/Video

Analyze a single image or video for AI-generated content.

```http
POST /analyze
```

#### Request

**Headers:**
```http
Content-Type: multipart/form-data
Authorization: Bearer YOUR_API_KEY
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Image or video file to analyze |
| `models` | Array | No | Specific models to use (`openai`, `gemini`, `anthropic`). Default: all |
| `webhook_url` | String | No | URL to receive result notification |
| `priority` | String | No | Processing priority: `low`, `normal`, `high`. Default: `normal` |

**Example Request:**
```bash
curl -X POST https://api.fakephoto.ai/v1/analyze \
  -H "Authorization: Bearer sk_live_1234567890" \
  -F "file=@/path/to/image.jpg" \
  -F "models=[\"openai\",\"gemini\"]" \
  -F "priority=high"
```

#### Response

**Status: 200 OK**

```json
{
  "id": "anal_1234567890",
  "status": "completed",
  "filename": "image.jpg",
  "content_type": "image/jpeg",
  "file_size": 2456789,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z",
  "result": {
    "is_ai_generated": true,
    "confidence_score": 87.5,
    "confidence_level": "high",
    "consensus": "strong",
    "model_results": {
      "openai": {
        "ai_probability": 0.92,
        "confidence": 0.85,
        "reasoning": "Unnatural lighting patterns detected in the subject's face. The shadow direction is inconsistent with the apparent light source.",
        "indicators": ["unnatural_lighting", "inconsistent_shadows"]
      },
      "gemini": {
        "ai_probability": 0.88,
        "confidence": 0.90,
        "reasoning": "Texture analysis reveals synthetic patterns typical of GAN-generated images.",
        "indicators": ["texture_anomalies", "repetitive_patterns"]
      },
      "anthropic": {
        "ai_probability": 0.85,
        "confidence": 0.82,
        "reasoning": "Metadata analysis shows no camera EXIF data. Color distribution is atypical for natural photography.",
        "indicators": ["missing_metadata", "unnatural_color_distribution"]
      }
    },
    "indicators": [
      "Unnatural lighting patterns",
      "Inconsistent shadow directions",
      "Synthetic texture details",
      "Missing EXIF metadata",
      "Repetitive background patterns"
    ],
    "recommendations": [
      "High probability of AI generation. Verify with additional forensic tools.",
      "Multiple AI indicators detected - high scrutiny warranted."
    ]
  },
  "processing_time_ms": 4523
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique analysis ID |
| `status` | String | `pending`, `processing`, `completed`, `failed` |
| `result.is_ai_generated` | Boolean | Whether content is likely AI-generated |
| `result.confidence_score` | Float | Overall confidence score (0-100) |
| `result.confidence_level` | String | `low` (<50), `medium` (50-75), `high` (>75) |
| `result.consensus` | String | Model agreement: `strong`, `moderate`, `weak` |
| `result.model_results` | Object | Individual results from each AI model |

---

### 2. Analyze by URL

Analyze an image or video hosted at a public URL.

```http
POST /analyze-url
```

#### Request

```json
{
  "url": "https://example.com/image.jpg",
  "models": ["openai", "gemini", "anthropic"],
  "webhook_url": "https://your-app.com/webhook"
}
```

#### Response

Same as `/analyze` endpoint.

---

### 3. Batch Analysis

Submit multiple files for batch processing.

```http
POST /batch
```

#### Request

**Headers:**
```http
Content-Type: multipart/form-data
Authorization: Bearer YOUR_API_KEY
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | Array[File] | Yes | Multiple image/video files |
| `models` | Array | No | Models to use |
| `webhook_url` | String | No | Notification URL |

**Example Request:**
```bash
curl -X POST https://api.fakephoto.ai/v1/batch \
  -H "Authorization: Bearer sk_live_1234567890" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.png" \
  -F "files=@/path/to/video.mp4"
```

#### Response

```json
{
  "batch_id": "batch_1234567890",
  "status": "queued",
  "total_files": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "files": [
    {
      "file_id": "file_abc123",
      "filename": "image1.jpg",
      "status": "queued"
    },
    {
      "file_id": "file_def456",
      "filename": "image2.png",
      "status": "queued"
    },
    {
      "file_id": "file_ghi789",
      "filename": "video.mp4",
      "status": "queued"
    }
  ]
}
```

---

### 4. Get Batch Status

Check the status of a batch processing job.

```http
GET /batch/{batch_id}
```

#### Response

```json
{
  "batch_id": "batch_1234567890",
  "status": "processing",
  "progress": {
    "total": 3,
    "completed": 1,
    "failed": 0,
    "pending": 2
  },
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:05Z",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "results": [
    {
      "file_id": "file_abc123",
      "filename": "image1.jpg",
      "status": "completed",
      "result": { /* Analysis result */ }
    },
    {
      "file_id": "file_def456",
      "filename": "image2.png",
      "status": "processing"
    }
  ]
}
```

---

### 5. Get Analysis Result

Retrieve a specific analysis by ID.

```http
GET /analysis/{analysis_id}
```

#### Response

Same format as `/analyze` response.

---

### 6. List Analyses

List all analyses for your account.

```http
GET /analyses
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | Integer | Max results (1-100, default: 20) |
| `cursor` | String | Pagination cursor |
| `status` | String | Filter by status |
| `from_date` | ISO8601 | Start date filter |
| `to_date` | ISO8601 | End date filter |

#### Response

```json
{
  "data": [
    {
      "id": "anal_1234567890",
      "status": "completed",
      "filename": "image.jpg",
      "created_at": "2024-01-15T10:30:00Z",
      "result": { /* Summary */ }
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNDV9",
    "has_more": true
  }
}
```

---

### 7. Health Check

Check API status and model availability.

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "openai": "available",
    "gemini": "available",
    "anthropic": "degraded"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "invalid_file_format",
    "message": "The provided file format is not supported.",
    "details": {
      "field": "file",
      "accepted_formats": ["jpg", "jpeg", "png", "webp", "heic", "mp4", "mov", "avi"]
    },
    "request_id": "req_1234567890",
    "documentation_url": "https://docs.fakephoto.ai/errors/invalid_file_format"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Invalid or missing API key |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Rate limit exceeded |
| `invalid_file_format` | 400 | Unsupported file format |
| `file_too_large` | 413 | File exceeds size limit (100MB) |
| `processing_error` | 500 | Internal processing error |
| `model_unavailable` | 503 | One or more AI models unavailable |

---

## Webhooks

Receive real-time notifications when analysis completes.

### Webhook Payload

```json
{
  "event": "analysis.completed",
  "timestamp": "2024-01-15T10:30:05Z",
  "data": {
    "analysis_id": "anal_1234567890",
    "status": "completed",
    "result": { /* Full analysis result */ }
  }
}
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `analysis.completed` | Analysis finished successfully |
| `analysis.failed` | Analysis failed |
| `batch.completed` | All batch items processed |
| `batch.progress` | Progress update for batch |

### Webhook Verification

Verify webhook authenticity using the signature:

```python
import hmac
import hashlib

signature = request.headers['X-Webhook-Signature']
payload = request.body
secret = b'your_webhook_secret'

expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
if hmac.compare_digest(signature, expected):
    # Webhook is authentic
    pass
```

---

## SDKs and Libraries

### Official SDKs

- **Python:** `pip install fakephoto-ai`
- **JavaScript/Node:** `npm install @fakephoto/api`
- **Go:** `go get github.com/fakephoto/go-sdk`

### Community SDKs

- **PHP:** `composer require fakephoto/api-client`
- **Ruby:** `gem install fakephoto`
- **Rust:** `cargo add fakephoto`

---

## Support

- **Documentation:** https://docs.fakephoto.ai
- **API Status:** https://status.fakephoto.ai
- **Support Email:** support@fakephoto.ai
- **Discord:** https://discord.gg/fakephoto

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial API release
- Multi-model analysis support
- Batch processing
- Webhook notifications
