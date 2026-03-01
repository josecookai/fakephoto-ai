"""Mock AI model clients for testing without actual API calls."""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from unittest.mock import MagicMock

from fakephoto.detector import ModelResult
from fakephoto.models.base import BaseModelClient


class MockOpenAIClient(BaseModelClient):
    """Mock OpenAI client for testing."""
    
    def __init__(
        self, 
        api_key: str,
        ai_probability: float = 0.5,
        confidence: float = 0.8,
        should_fail: bool = False,
        failure_exception: Optional[Exception] = None,
        latency_ms: float = 100.0,
    ):
        self.api_key = api_key
        self.model_name = "openai"
        self._ai_probability = ai_probability
        self._confidence = confidence
        self._should_fail = should_fail
        self._failure_exception = failure_exception or RuntimeError("Mock API error")
        self._latency_ms = latency_ms
        self.call_count = 0
        self.last_frames: Optional[List[Path]] = None
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Return mock analysis result."""
        self.call_count += 1
        self.last_frames = frames
        
        if self._should_fail:
            raise self._failure_exception
        
        return ModelResult(
            model_name=self.model_name,
            ai_probability=self._ai_probability,
            confidence=self._confidence,
            reasoning=f"Mock OpenAI analysis with probability {self._ai_probability}",
            indicators=self._get_indicators(),
        )
    
    def _get_indicators(self) -> List[str]:
        """Generate mock indicators based on probability."""
        if self._ai_probability > 0.7:
            return ["Unnatural lighting", "Texture inconsistencies", "AI artifacts"]
        elif self._ai_probability > 0.4:
            return ["Possible texture issues"]
        return []


class MockGeminiClient(BaseModelClient):
    """Mock Google Gemini client for testing."""
    
    def __init__(
        self,
        api_key: str,
        ai_probability: float = 0.5,
        confidence: float = 0.8,
        should_fail: bool = False,
        failure_exception: Optional[Exception] = None,
    ):
        self.api_key = api_key
        self.model_name = "gemini"
        self._ai_probability = ai_probability
        self._confidence = confidence
        self._should_fail = should_fail
        self._failure_exception = failure_exception or RuntimeError("Mock Gemini API error")
        self.call_count = 0
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Return mock analysis result."""
        self.call_count += 1
        
        if self._should_fail:
            raise self._failure_exception
        
        return ModelResult(
            model_name=self.model_name,
            ai_probability=self._ai_probability,
            confidence=self._confidence,
            reasoning=f"Mock Gemini analysis: {'AI' if self._ai_probability > 0.5 else 'Real'}",
            indicators=self._get_indicators(),
        )
    
    def _get_indicators(self) -> List[str]:
        """Generate mock indicators."""
        indicators_pool = [
            "Unnatural lighting",
            "Texture inconsistencies",
            "Facial anomalies",
            "AI artifacts",
            "Compression anomalies",
        ]
        if self._ai_probability > 0.6:
            return random.sample(indicators_pool, k=min(3, len(indicators_pool)))
        return []


class MockAnthropicClient(BaseModelClient):
    """Mock Anthropic Claude client for testing."""
    
    def __init__(
        self,
        api_key: str,
        ai_probability: float = 0.5,
        confidence: float = 0.8,
        should_fail: bool = False,
        failure_exception: Optional[Exception] = None,
    ):
        self.api_key = api_key
        self.model_name = "anthropic"
        self._ai_probability = ai_probability
        self._confidence = confidence
        self._should_fail = should_fail
        self._failure_exception = failure_exception or RuntimeError("Mock Anthropic API error")
        self.call_count = 0
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Return mock analysis result."""
        self.call_count += 1
        
        if self._should_fail:
            raise self._failure_exception
        
        return ModelResult(
            model_name=self.model_name,
            ai_probability=self._ai_probability,
            confidence=self._confidence,
            reasoning=f"Mock Claude analysis result: {self._ai_probability:.2f}",
            indicators=self._get_indicators(),
        )
    
    def _get_indicators(self) -> List[str]:
        """Generate mock indicators."""
        if self._ai_probability > 0.75:
            return ["Strong AI indicators", "Unnatural patterns"]
        elif self._ai_probability > 0.5:
            return ["Possible AI artifacts"]
        return ["Appears authentic"]


class FailingClient(BaseModelClient):
    """Client that always fails - for testing error handling."""
    
    def __init__(self, api_key: str, error_message: str = "Always fails"):
        self.api_key = api_key
        self.model_name = "failing"
        self._error_message = error_message
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Always raises an exception."""
        raise RuntimeError(self._error_message)


class SlowClient(BaseModelClient):
    """Client that responds slowly - for testing timeouts."""
    
    def __init__(self, api_key: str, delay_ms: float = 5000):
        self.api_key = api_key
        self.model_name = "slow"
        self._delay_ms = delay_ms
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Simulate slow response."""
        import time
        time.sleep(self._delay_ms / 1000)
        return ModelResult(
            model_name=self.model_name,
            ai_probability=0.5,
            confidence=0.5,
            reasoning="Slow response",
            indicators=[],
        )


class VariableResponseClient(BaseModelClient):
    """Client that returns variable responses - for testing aggregation."""
    
    def __init__(
        self, 
        api_key: str, 
        responses: Optional[List[ModelResult]] = None
    ):
        self.api_key = api_key
        self.model_name = "variable"
        self._responses = responses or []
        self._response_index = 0
    
    def analyze(self, frames: List[Path]) -> ModelResult:
        """Return next response in sequence."""
        if self._response_index < len(self._responses):
            response = self._responses[self._response_index]
            self._response_index += 1
            return response
        
        # Default response if sequence exhausted
        return ModelResult(
            model_name=self.model_name,
            ai_probability=0.5,
            confidence=0.5,
            reasoning="Default response",
            indicators=[],
        )
    
    def reset(self):
        """Reset response counter."""
        self._response_index = 0


def create_mock_response_from_file(
    response_file: Path,
    provider: str = "openai"
) -> Dict[str, Any]:
    """Load a mock API response from JSON file."""
    with open(response_file, 'r') as f:
        return json.load(f)


def create_sequential_mock_client(
    api_key: str,
    probabilities: List[float],
    provider: str = "openai"
) -> BaseModelClient:
    """Create a mock client that returns sequential probabilities."""
    responses = [
        ModelResult(
            model_name=provider,
            ai_probability=p,
            confidence=0.8,
            reasoning=f"Sequential result {i}: {p}",
            indicators=["Test indicator"] if p > 0.5 else [],
        )
        for i, p in enumerate(probabilities)
    ]
    return VariableResponseClient(api_key, responses)


def patch_model_clients(detector_class):
    """Context manager/decorator to patch all model clients."""
    from unittest.mock import patch
    
    patches = [
        patch(f"{detector_class.__module__}.OpenAIClient"),
        patch(f"{detector_class.__module__}.GeminiClient"),
        patch(f"{detector_class.__module__}.AnthropicClient"),
    ]
    return patches
