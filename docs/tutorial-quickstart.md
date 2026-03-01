# FakePhoto.ai - 5-Minute Quick Start Guide

Get up and running with FakePhoto.ai in just 5 minutes! This guide will walk you through analyzing your first image for AI-generated content.

---

## Prerequisites

- Python 3.11 or higher
- API keys from at least one provider:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Google AI Studio](https://makersuite.google.com/app/apikey)
  - [Anthropic](https://console.anthropic.com/settings/keys)

---

## Step 1: Installation (1 minute)

Install FakePhoto.ai using pip:

```bash
pip install fakephoto-ai
```

Or install from source:

```bash
git clone https://github.com/josecookai/fakephoto-ai.git
cd fakephoto-ai
pip install -e .
```

---

## Step 2: Set Up API Keys (1 minute)

Create a `.env` file in your project directory:

```bash
touch .env
```

Add your API keys (you need at least one):

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

> 💡 **Tip:** Using multiple API keys gives you better accuracy through ensemble analysis!

---

## Step 3: Analyze Your First Image (2 minutes)

### Option A: Command Line (Quickest)

```bash
# Set environment variable temporarily
export OPENAI_API_KEY="sk-your-key-here"

# Analyze an image
fakephoto analyze /path/to/your/image.jpg
```

**Example output:**

```
🖼️  Analyzing: vacation_photo.jpg
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Results:
   AI Generated: YES ⚠️
   Confidence: 87.5%
   Consensus: Strong

🔍 Indicators Detected:
   • Unnatural lighting patterns
   • Inconsistent shadow directions
   • Missing EXIF metadata

⚡ Model Breakdown:
   • OpenAI: 92% AI probability
   • Gemini: 88% AI probability
   • Anthropic: 85% AI probability

💡 Recommendations:
   • High probability of AI generation. Verify with additional tools.
   • Multiple AI indicators detected - high scrutiny warranted.
```

### Option B: Python Script

Create `analyze.py`:

```python
from fakephoto import MultiModelDetector
from dotenv import load_dotenv
import os

# Load API keys from .env
load_dotenv()

# Initialize detector
detector = MultiModelDetector(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Analyze image
result = detector.analyze("/path/to/your/image.jpg")

# Print results
print(f"File: {result.filename}")
print(f"AI Generated: {'YES ⚠️' if result.is_ai_generated else 'NO ✓'}")
print(f"Confidence: {result.confidence_score:.1f}%")
print(f"Consensus: {result.consensus}")

print("\nIndicators:")
for indicator in result.indicators:
    print(f"  • {indicator}")

print("\nRecommendations:")
for rec in result.recommendations:
    print(f"  • {rec}")
```

Run it:

```bash
python analyze.py
```

---

## Step 4: Try Batch Processing (1 minute)

Analyze multiple images at once:

```bash
# Analyze all images in a folder
fakephoto analyze-batch /path/to/folder/
```

Or in Python:

```python
results = detector.analyze_batch("/path/to/folder/")

for result in results:
    status = "⚠️ AI" if result.is_ai_generated else "✓ Authentic"
    print(f"{result.filename}: {status} ({result.confidence_score:.1f}%)")
```

---

## What's Next?

🎉 Congratulations! You've successfully analyzed your first image.

### Quick Next Steps:

1. **Try the Web Interface**
   ```bash
   streamlit run -m fakephoto.app
   ```

2. **Read the Full Tutorial**
   - [Python SDK Tutorial](tutorial-python.md)
   - [REST API Tutorial](tutorial-api.md)
   - [Batch Processing Guide](tutorial-batch.md)

3. **Explore Use Cases**
   - [Journalist Workflow](../examples/journalist-workflow.md)
   - [Social Media Moderation](../examples/social-media-moderation.md)

4. **Join the Community**
   - GitHub Discussions: https://github.com/josecookai/fakephoto-ai/discussions
   - Discord: https://discord.gg/fakephoto

---

## Troubleshooting

### "No API keys provided"
Make sure you've set at least one API key in your environment or `.env` file.

### "File not found"
Use the full path to your image or ensure you're in the correct directory.

### "Rate limit exceeded"
You've hit the API rate limit. Wait a moment and try again, or upgrade your API tier.

---

## One-Liner for the Impatient

```bash
pip install fakephoto-ai && export OPENAI_API_KEY="your-key" && python -c "from fakephoto import analyze_image; print(analyze_image('image.jpg'))"
```

Happy detecting! 🔍
