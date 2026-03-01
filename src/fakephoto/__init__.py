"""
FakePhoto.ai - Multi-Model AI Detection Engine

Verify if images and videos are AI-generated using 
OpenAI GPT-4V, Google Gemini, and Anthropic Claude.
"""

__version__ = "0.1.0"
__author__ = "FakePhoto.ai Team"

from .detector import MultiModelDetector, DetectionResult, analyze_image

__all__ = [
    "MultiModelDetector",
    "DetectionResult",
    "analyze_image",
]
