"""Test utilities and helper functions."""

import os
import json
import hashlib
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from contextlib import contextmanager
from dataclasses import asdict
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from fakephoto.detector import DetectionResult, ModelResult


def create_test_image(
    path: Path,
    width: int = 100,
    height: int = 100,
    mode: str = "RGB",
    color: Tuple[int, ...] = (255, 0, 0),
) -> Path:
    """Create a simple test image."""
    img = Image.new(mode, (width, height), color)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def create_test_image_with_metadata(
    path: Path,
    width: int = 100,
    height: int = 100,
    exif_data: Optional[Dict[str, Any]] = None,
) -> Path:
    """Create a test image with EXIF metadata."""
    img = Image.new("RGB", (width, height), (100, 150, 200))
    
    # Add basic EXIF if requested
    if exif_data:
        from PIL.ExifTags import TAGS
        exif = img._getexif() or {}
        for key, value in exif_data.items():
            exif[TAGS.get(key, key)] = value
        img.save(path, exif=exif)
    else:
        img.save(path)
    
    return path


def create_ai_like_image(path: Path, width: int = 1024, height: int = 1024) -> Path:
    """Create an image that simulates AI-generated characteristics."""
    # AI images often have specific dimensions and characteristics
    img = Image.new("RGB", (width, height), (128, 128, 128))
    draw = ImageDraw.Draw(img)
    
    # Add some repetitive patterns (common in AI images)
    for i in range(0, width, 50):
        for j in range(0, height, 50):
            color = (200, 200, 200) if (i + j) % 100 == 0 else (100, 100, 100)
            draw.rectangle([i, j, i + 25, j + 25], fill=color)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=95)
    return path


def create_real_like_image(path: Path, width: int = 1920, height: int = 1080) -> Path:
    """Create an image that simulates real photo characteristics."""
    # Simulate natural photo with noise
    img_array = np.random.normal(128, 20, (height, width, 3)).astype(np.uint8)
    img = Image.fromarray(img_array)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=85)
    return path


def generate_test_video(
    path: Path,
    duration_seconds: float = 1.0,
    fps: int = 30,
    width: int = 640,
    height: int = 480,
) -> Path:
    """Generate a simple test video file using OpenCV."""
    try:
        import cv2
    except ImportError:
        # Create a placeholder if OpenCV not available
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"mock video content")
        return path
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    
    num_frames = int(duration_seconds * fps)
    for i in range(num_frames):
        # Create gradient frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = [i % 255, (i * 2) % 255, (i * 3) % 255]
        out.write(frame)
    
    out.release()
    return path


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_mock_response(filename: str, fixtures_dir: Path) -> Dict[str, Any]:
    """Load a mock API response from fixtures."""
    response_path = fixtures_dir / "mock-api-responses" / filename
    with open(response_path, 'r') as f:
        return json.load(f)


def assert_detection_result_valid(result: DetectionResult) -> None:
    """Assert that a DetectionResult is valid."""
    assert isinstance(result, DetectionResult)
    assert result.filename
    assert isinstance(result.is_ai_generated, bool)
    assert 0 <= result.confidence_score <= 100
    assert result.consensus in ['strong', 'moderate', 'weak']
    assert isinstance(result.indicators, list)
    assert isinstance(result.recommendations, list)
    assert isinstance(result.model_scores, dict)


def assert_model_result_valid(result: ModelResult) -> None:
    """Assert that a ModelResult is valid."""
    assert isinstance(result, ModelResult)
    assert result.model_name
    assert 0 <= result.ai_probability <= 1
    assert 0 <= result.confidence <= 1
    assert isinstance(result.reasoning, str)
    assert isinstance(result.indicators, list)


def results_agree(result1: ModelResult, result2: ModelResult, tolerance: float = 0.2) -> bool:
    """Check if two model results agree within tolerance."""
    return abs(result1.ai_probability - result2.ai_probability) <= tolerance


@contextmanager
def temp_directory():
    """Context manager for temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@contextmanager
def temp_file(content: bytes = b"", suffix: str = ".tmp"):
    """Context manager for temporary file."""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)
    try:
        yield path
    finally:
        if path.exists():
            path.unlink()


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(self):
        self.elapsed_ms: float = 0
        self._start: Optional[float] = None
    
    def __enter__(self):
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        end = time.perf_counter()
        self.elapsed_ms = (end - self._start) * 1000


def retry(
    func,
    max_attempts: int = 3,
    delay_ms: float = 100,
    exceptions: Tuple[type, ...] = (Exception,)
):
    """Retry a function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep((delay_ms * (2 ** attempt)) / 1000)


def generate_batch_test_images(
    directory: Path,
    count: int,
    prefix: str = "test",
    width: int = 100,
    height: int = 100,
) -> List[Path]:
    """Generate a batch of test images with different characteristics."""
    paths = []
    for i in range(count):
        path = directory / f"{prefix}_{i:04d}.jpg"
        color = (
            (i * 50) % 256,
            (i * 100) % 256,
            (i * 150) % 256,
        )
        create_test_image(path, width, height, color=color)
        paths.append(path)
    return paths


def detection_result_to_dict(result: DetectionResult) -> Dict[str, Any]:
    """Convert DetectionResult to dictionary (for serialization)."""
    return {
        "filename": result.filename,
        "is_ai_generated": result.is_ai_generated,
        "confidence_score": result.confidence_score,
        "model_scores": result.model_scores,
        "consensus": result.consensus,
        "indicators": result.indicators,
        "recommendations": result.recommendations,
    }


def create_confusion_matrix(
    predictions: List[bool],
    ground_truth: List[bool],
) -> Dict[str, int]:
    """Create confusion matrix from predictions."""
    assert len(predictions) == len(ground_truth)
    
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p and g)
    tn = sum(1 for p, g in zip(predictions, ground_truth) if not p and not g)
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p and not g)
    fn = sum(1 for p, g in zip(predictions, ground_truth) if not p and g)
    
    return {
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
    }


def calculate_metrics(confusion_matrix: Dict[str, int]) -> Dict[str, float]:
    """Calculate metrics from confusion matrix."""
    tp = confusion_matrix["true_positive"]
    tn = confusion_matrix["true_negative"]
    fp = confusion_matrix["false_positive"]
    fn = confusion_matrix["false_negative"]
    
    total = tp + tn + fp + fn
    
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def set_api_keys_env(mock_keys: Dict[str, str]):
    """Set API keys in environment variables."""
    for key, value in mock_keys.items():
        env_key = key.upper().replace("_API_KEY", "_API_KEY")
        os.environ[env_key] = value


def clear_api_keys_env():
    """Clear API keys from environment variables."""
    keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"]
    for key in keys:
        os.environ.pop(key, None)
