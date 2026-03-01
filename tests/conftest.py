"""Pytest configuration and shared fixtures for FakePhoto.ai tests."""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Generator, List, Dict, Any
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, asdict

import pytest
import numpy as np
from PIL import Image

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fakephoto.detector import (
    MultiModelDetector,
    DetectionResult,
    ModelResult,
)
from fakephoto.models.base import BaseModelClient


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def tests_dir(project_root: Path) -> Path:
    """Return tests directory."""
    return project_root / "tests"


@pytest.fixture
def fixtures_dir(tests_dir: Path) -> Path:
    """Return fixtures directory."""
    return tests_dir / "fixtures"


@pytest.fixture
def sample_images_dir(fixtures_dir: Path) -> Path:
    """Return sample images directory."""
    return fixtures_dir / "sample-real-images"


@pytest.fixture
def sample_ai_images_dir(fixtures_dir: Path) -> Path:
    """Return sample AI images directory."""
    return fixtures_dir / "sample-ai-images"


@pytest.fixture
def sample_videos_dir(fixtures_dir: Path) -> Path:
    """Return sample videos directory."""
    return fixtures_dir / "sample-videos"


@pytest.fixture
def mock_responses_dir(fixtures_dir: Path) -> Path:
    """Return mock API responses directory."""
    return fixtures_dir / "mock-api-responses"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# Image/Video Fixtures
# ============================================================================

@pytest.fixture
def create_test_image():
    """Factory fixture to create test images with various properties."""
    def _create(
        path: Path,
        width: int = 100,
        height: int = 100,
        mode: str = "RGB",
        color: tuple = (255, 0, 0),
    ) -> Path:
        """Create a test image file."""
        img = Image.new(mode, (width, height), color)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        return path
    return _create


@pytest.fixture
def real_image_path(temp_dir: Path, create_test_image) -> Path:
    """Create a sample real-looking image."""
    return create_test_image(
        temp_dir / "real_image.jpg",
        width=1920,
        height=1080,
        color=(100, 150, 200),
    )


@pytest.fixture
def ai_image_path(temp_dir: Path, create_test_image) -> Path:
    """Create a sample AI-looking image (often different characteristics)."""
    return create_test_image(
        temp_dir / "ai_image.png",
        width=1024,
        height=1024,
        color=(200, 200, 200),
    )


@pytest.fixture
def small_image_path(temp_dir: Path, create_test_image) -> Path:
    """Create a very small image."""
    return create_test_image(
        temp_dir / "small_image.jpg",
        width=10,
        height=10,
    )


@pytest.fixture
def large_image_path(temp_dir: Path, create_test_image) -> Path:
    """Create a very large image."""
    return create_test_image(
        temp_dir / "large_image.jpg",
        width=8000,
        height=6000,
    )


@pytest.fixture
def transparent_image_path(temp_dir: Path) -> Path:
    """Create an image with transparency."""
    path = temp_dir / "transparent.png"
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


@pytest.fixture
def grayscale_image_path(temp_dir: Path) -> Path:
    """Create a grayscale image."""
    path = temp_dir / "grayscale.jpg"
    img = Image.new("L", (100, 100), 128)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_model_result() -> ModelResult:
    """Return a sample ModelResult."""
    return ModelResult(
        model_name="openai",
        ai_probability=0.8,
        confidence=0.9,
        reasoning="Detected unnatural lighting patterns",
        indicators=["Unnatural lighting", "Texture inconsistencies"],
    )


@pytest.fixture
def mock_detection_result() -> DetectionResult:
    """Return a sample DetectionResult."""
    return DetectionResult(
        filename="test_image.jpg",
        is_ai_generated=True,
        confidence_score=75.0,
        model_scores={
            "openai": {"ai_probability": 0.8, "confidence": 0.9},
            "gemini": {"ai_probability": 0.7, "confidence": 0.85},
        },
        consensus="moderate",
        indicators=["Unnatural lighting", "Texture inconsistencies"],
        recommendations=["Verify with additional tools"],
    )


@pytest.fixture
def mock_api_keys() -> Dict[str, str]:
    """Return mock API keys for testing."""
    return {
        "openai_api_key": "sk-test-openai123456789",
        "google_api_key": "test-google-api-key-12345",
        "anthropic_api_key": "sk-ant-test-key-12345",
    }


@pytest.fixture
def mock_openai_response() -> Dict[str, Any]:
    """Return mock OpenAI API response."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "gpt-4-vision-preview",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Based on my analysis, this image shows signs of AI generation with 80% probability. Unnatural lighting patterns detected.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    }


@pytest.fixture
def mock_gemini_response() -> Dict[str, Any]:
    """Return mock Gemini API response."""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "AI-generated: 70% confidence. Found texture anomalies."
                        }
                    ]
                },
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 20},
    }


@pytest.fixture
def mock_anthropic_response() -> Dict[str, Any]:
    """Return mock Anthropic API response."""
    return {
        "id": "msg_01234567890ABCDEF",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Analysis indicates possible AI generation (65% probability). Minor facial asymmetry detected.",
            }
        ],
        "model": "claude-3-opus-20240229",
        "usage": {"input_tokens": 100, "output_tokens": 30},
    }


# ============================================================================
# Mock Client Fixtures
# ============================================================================

class MockModelClient(BaseModelClient):
    """Mock model client for testing."""
    
    def __init__(self, api_key: str, model_name: str = "mock", 
                 ai_probability: float = 0.5, confidence: float = 0.8):
        self.api_key = api_key
        self.model_name = model_name
        self._ai_probability = ai_probability
        self._confidence = confidence
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Return mock analysis result."""
        from fakephoto.detector import ModelResult
        return ModelResult(
            model_name=self.model_name,
            ai_probability=self._ai_probability,
            confidence=self._confidence,
            reasoning=f"Mock analysis from {self.model_name}",
            indicators=["Mock indicator"],
        )


@pytest.fixture
def mock_client():
    """Return MockModelClient class."""
    return MockModelClient


@pytest.fixture
def mock_detector(mock_api_keys: Dict[str, str]) -> MultiModelDetector:
    """Create a detector with mocked clients."""
    with patch("fakephoto.detector.OpenAIClient") as mock_openai, \
         patch("fakephoto.detector.GeminiClient") as mock_gemini, \
         patch("fakephoto.detector.AnthropicClient") as mock_anthropic:
        
        mock_openai.return_value = MockModelClient(
            mock_api_keys["openai_api_key"], "openai", 0.8, 0.9
        )
        mock_gemini.return_value = MockModelClient(
            mock_api_keys["google_api_key"], "gemini", 0.7, 0.85
        )
        mock_anthropic.return_value = MockModelClient(
            mock_api_keys["anthropic_api_key"], "anthropic", 0.6, 0.8
        )
        
        detector = MultiModelDetector(**mock_api_keys)
        return detector


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def clean_env():
    """Clean environment variables fixture."""
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def env_with_mock_keys(monkeypatch, mock_api_keys):
    """Set up environment with mock API keys."""
    for key, value in mock_api_keys.items():
        env_key = key.upper().replace("_API_KEY", "_API_KEY")
        monkeypatch.setenv(env_key, value)
    yield


# ============================================================================
# Test Data Generators
# ============================================================================

@pytest.fixture
def generate_random_image_batch(temp_dir: Path, create_test_image):
    """Generate a batch of random test images."""
    def _generate(count: int = 5) -> List[Path]:
        paths = []
        for i in range(count):
            path = temp_dir / f"batch_image_{i}.jpg"
            color = tuple(np.random.randint(0, 256, 3).tolist())
            create_test_image(path, width=100, height=100, color=color)
            paths.append(path)
        return paths
    return _generate


@pytest.fixture
def sample_model_results() -> List[ModelResult]:
    """Return a list of sample model results."""
    return [
        ModelResult(
            model_name="openai",
            ai_probability=0.9,
            confidence=0.95,
            reasoning="Strong AI indicators",
            indicators=["Unnatural lighting", "Texture issues"],
        ),
        ModelResult(
            model_name="gemini",
            ai_probability=0.85,
            confidence=0.9,
            reasoning="Likely AI-generated",
            indicators=["Facial anomalies"],
        ),
        ModelResult(
            model_name="anthropic",
            ai_probability=0.3,
            confidence=0.7,
            reasoning="Appears authentic",
            indicators=[],
        ),
    ]
