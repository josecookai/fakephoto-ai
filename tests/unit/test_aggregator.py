"""Unit tests for the confidence aggregation logic."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fakephoto.detector import (
    MultiModelDetector,
    DetectionResult,
    ModelResult,
)


@pytest.mark.unit
class TestAggregationBasics:
    """Test basic aggregation functionality."""
    
    @pytest.fixture
    def detector(self, mock_api_keys):
        """Create detector for aggregation tests."""
        with patch("fakephoto.detector.OpenAIClient") as mock_client:
            mock_client.return_value = MagicMock()
            yield MultiModelDetector(
                openai_api_key=mock_api_keys["openai_api_key"]
            )
    
    def test_aggregate_single_model(self, detector):
        """Test aggregation with single model result."""
        results = [
            ModelResult("openai", 0.8, 0.9, "AI detected", ["artifact"])
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        
        assert aggregated.filename == "test.jpg"
        assert aggregated.confidence_score == pytest.approx(80.0)
        assert aggregated.is_ai_generated is True
        assert aggregated.consensus == "strong"
    
    def test_aggregate_multiple_models(self, detector):
        """Test aggregation with multiple model results."""
        results = [
            ModelResult("openai", 0.9, 0.95, "AI", ["lighting"]),
            ModelResult("gemini", 0.8, 0.9, "AI", ["texture"]),
            ModelResult("anthropic", 0.85, 0.88, "AI", ["artifacts"]),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        
        # Weighted average: (0.9*0.95 + 0.8*0.9 + 0.85*0.88) / (0.95 + 0.9 + 0.88)
        # = (0.855 + 0.72 + 0.748) / 2.73 = 2.323 / 2.73 ≈ 0.851
        expected_prob = (0.9 * 0.95 + 0.8 * 0.9 + 0.85 * 0.88) / (0.95 + 0.9 + 0.88)
        assert aggregated.confidence_score == pytest.approx(expected_prob * 100, rel=0.01)
        assert aggregated.consensus == "strong"
    
    def test_aggregate_empty_results_raises(self, detector):
        """Test that empty results raises ValueError."""
        with pytest.raises(ValueError, match="No model results"):
            detector._aggregate_results("test.jpg", [])


@pytest.mark.unit
class TestConsensusCalculation:
    """Test consensus level calculation."""
    
    @pytest.fixture
    def detector(self, mock_api_keys):
        """Create detector with 0.7 threshold."""
        with patch("fakephoto.detector.OpenAIClient") as mock_client:
            mock_client.return_value = MagicMock()
            yield MultiModelDetector(
                openai_api_key=mock_api_keys["openai_api_key"],
                confidence_threshold=0.7
            )
    
    def test_strong_consensus_all_agree(self, detector):
        """Test strong consensus when all models agree."""
        results = [
            ModelResult("openai", 0.8, 0.9, "AI", []),
            ModelResult("gemini", 0.75, 0.85, "AI", []),
            ModelResult("anthropic", 0.85, 0.9, "AI", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        assert aggregated.consensus == "strong"
        assert aggregated.is_ai_generated is True
    
    def test_moderate_consensus_majority(self, detector):
        """Test moderate consensus when majority agrees."""
        results = [
            ModelResult("openai", 0.8, 0.9, "AI", []),
            ModelResult("gemini", 0.75, 0.85, "AI", []),
            ModelResult("anthropic", 0.3, 0.8, "Real", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        assert aggregated.consensus == "moderate"
        assert aggregated.is_ai_generated is True  # Weighted avg > 0.7
    
    def test_weak_consensus_split(self, detector):
        """Test weak consensus when models disagree."""
        results = [
            ModelResult("openai", 0.8, 0.9, "AI", []),
            ModelResult("gemini", 0.3, 0.85, "Real", []),
            ModelResult("anthropic", 0.2, 0.8, "Real", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        assert aggregated.consensus == "weak"
    
    def test_weak_consensus_all_disagree(self, detector):
        """Test weak consensus when all models say not AI."""
        results = [
            ModelResult("openai", 0.3, 0.9, "Real", []),
            ModelResult("gemini", 0.2, 0.85, "Real", []),
            ModelResult("anthropic", 0.4, 0.8, "Real", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        assert aggregated.consensus == "weak"
        assert aggregated.is_ai_generated is False


@pytest.mark.unit
class TestWeightedCalculation:
    """Test weighted probability calculation."""
    
    @pytest.fixture
    def detector(self, mock_api_keys):
        """Create detector for weighted tests."""
        with patch("fakephoto.detector.OpenAIClient") as mock_client:
            mock_client.return_value = MagicMock()
            yield MultiModelDetector(
                openai_api_key=mock_api_keys["openai_api_key"]
            )
    
    def test_high_confidence_weights_more(self, detector):
        """Test that high confidence models have more weight."""
        results = [
            ModelResult("openai", 0.9, 0.99, "AI", []),  # Very confident
            ModelResult("gemini", 0.3, 0.5, "Real", []),  # Low confidence
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        
        # High confidence model should dominate
        # Weighted: (0.9*0.99 + 0.3*0.5) / (0.99 + 0.5) = (0.891 + 0.15) / 1.49 ≈ 0.698
        expected = (0.9 * 0.99 + 0.3 * 0.5) / (0.99 + 0.5)
        assert aggregated.confidence_score / 100 == pytest.approx(expected, rel=0.01)
    
    def test_equal_weights_same_probability(self, detector):
        """Test equal weights when confidences are equal."""
        results = [
            ModelResult("openai", 0.8, 0.9, "AI", []),
            ModelResult("gemini", 0.4, 0.9, "Real", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        
        # Equal weights: (0.8 + 0.4) / 2 = 0.6
        assert aggregated.confidence_score == pytest.approx(60.0)


@pytest.mark.unit
class TestIndicatorAggregation:
    """Test indicator collection from multiple models."""
    
    @pytest.fixture
    def detector(self, mock_api_keys):
        """Create detector for indicator tests."""
        with patch("fakephoto.detector.OpenAIClient") as mock_client:
            mock_client.return_value = MagicMock()
            yield MultiModelDetector(
                openai_api_key=mock_api_keys["openai_api_key"]
            )
    
    def test_indicators_combined(self, detector):
        """Test that indicators from all models are combined."""
        results = [
            ModelResult("openai", 0.8, 0.9, "AI", ["lighting", "texture"]),
            ModelResult("gemini", 0.7, 0.85, "AI", ["texture", "artifacts"]),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        
        assert "lighting" in aggregated.indicators
        assert "texture" in aggregated.indicators
        assert "artifacts" in aggregated.indicators
        # Should have 3 unique indicators
        assert len(aggregated.indicators) == 3
    
    def test_empty_indicators(self, detector):
        """Test handling of empty indicators."""
        results = [
            ModelResult("openai", 0.3, 0.9, "Real", []),
            ModelResult("gemini", 0.2, 0.85, "Real", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        assert aggregated.indicators == []


@pytest.mark.unit
class TestRecommendations:
    """Test recommendation generation."""
    
    @pytest.fixture
    def detector(self, mock_api_keys):
        """Create detector for recommendation tests."""
        with patch("fakephoto.detector.OpenAIClient") as mock_client:
            mock_client.return_value = MagicMock()
            yield MultiModelDetector(
                openai_api_key=mock_api_keys["openai_api_key"]
            )
    
    def test_high_probability_recommendation(self, detector):
        """Test recommendations for high AI probability."""
        recs = detector._generate_recommendations(
            0.85, "strong", ["artifact"]
        )
        
        assert any("High probability" in r for r in recs)
        assert any("verify" in r.lower() for r in recs)
    
    def test_medium_probability_recommendation(self, detector):
        """Test recommendations for medium probability."""
        recs = detector._generate_recommendations(
            0.6, "moderate", ["artifact"]
        )
        
        assert any("Possible" in r for r in recs)
        assert any("Manual review" in r for r in recs)
    
    def test_low_probability_recommendation(self, detector):
        """Test recommendations for low probability."""
        recs = detector._generate_recommendations(
            0.3, "weak", []
        )
        
        assert any("Likely authentic" in r for r in recs)
    
    def test_weak_consensus_warning(self, detector):
        """Test that weak consensus generates warning."""
        recs = detector._generate_recommendations(
            0.5, "weak", ["artifact"]
        )
        
        assert any("Low model consensus" in r for r in recs)
    
    def test_many_indicators_warning(self, detector):
        """Test warning when many indicators detected."""
        indicators = ["i1", "i2", "i4", "i4"]
        recs = detector._generate_recommendations(
            0.7, "moderate", indicators
        )
        
        assert any("Multiple AI indicators" in r for r in recs)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases in aggregation."""
    
    @pytest.fixture
    def detector(self, mock_api_keys):
        """Create detector for edge case tests."""
        with patch("fakephoto.detector.OpenAIClient") as mock_client:
            mock_client.return_value = MagicMock()
            yield MultiModelDetector(
                openai_api_key=mock_api_keys["openai_api_key"]
            )
    
    def test_boundary_threshold(self, detector):
        """Test exactly at threshold boundary."""
        results = [
            ModelResult("openai", 0.7, 1.0, "Borderline", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        assert aggregated.confidence_score == pytest.approx(70.0)
        # Exactly at threshold - behavior depends on > vs >=
        # Current implementation uses > threshold
        assert aggregated.is_ai_generated is False
    
    def test_all_zero_confidence(self, detector):
        """Test handling of zero confidence (edge case)."""
        results = [
            ModelResult("openai", 0.5, 0.0, "Uncertain", []),
        ]
        
        # This would cause division by zero in weighted average
        # Implementation should handle this gracefully
        aggregated = detector._aggregate_results("test.jpg", results)
        assert isinstance(aggregated, DetectionResult)
    
    def test_very_different_probabilities(self, detector):
        """Test with very different model predictions."""
        results = [
            ModelResult("openai", 0.99, 0.95, "Definitely AI", []),
            ModelResult("gemini", 0.01, 0.95, "Definitely Real", []),
        ]
        
        aggregated = detector._aggregate_results("test.jpg", results)
        
        # With equal high confidence, should average to ~0.5
        assert aggregated.confidence_score == pytest.approx(50.0, abs=5.0)
        assert aggregated.consensus == "weak"
