"""
Unit tests for the detector module
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fakephoto.detector import (
    MultiModelDetector,
    DetectionResult,
    ModelResult,
    analyze_image
)


class TestModelResult:
    """Tests for ModelResult dataclass"""
    
    def test_model_result_creation(self):
        """Test creating a ModelResult"""
        result = ModelResult(
            model_name="test_model",
            ai_probability=0.8,
            confidence=0.9,
            reasoning="Test reasoning",
            indicators=["indicator1", "indicator2"]
        )
        
        assert result.model_name == "test_model"
        assert result.ai_probability == 0.8
        assert result.confidence == 0.9
        assert result.reasoning == "Test reasoning"
        assert len(result.indicators) == 2
    
    def test_model_result_probability_bounds(self):
        """Test probability values are within bounds"""
        result = ModelResult(
            model_name="test",
            ai_probability=0.5,
            confidence=0.5,
            reasoning="test",
            indicators=[]
        )
        
        assert 0.0 <= result.ai_probability <= 1.0
        assert 0.0 <= result.confidence <= 1.0


class TestDetectionResult:
    """Tests for DetectionResult dataclass"""
    
    def test_detection_result_creation(self):
        """Test creating a DetectionResult"""
        result = DetectionResult(
            filename="test.jpg",
            is_ai_generated=True,
            confidence_score=85.5,
            model_scores={"model1": {"ai_probability": 0.8, "confidence": 0.9}},
            consensus="strong",
            indicators=["indicator1"],
            recommendations=["recommendation1"]
        )
        
        assert result.filename == "test.jpg"
        assert result.is_ai_generated is True
        assert result.confidence_score == 85.5
        assert result.consensus == "strong"


class TestMultiModelDetectorInit:
    """Tests for detector initialization"""
    
    def test_init_no_api_keys(self):
        """Test that detector requires at least one API key"""
        with pytest.raises(ValueError, match="At least one API key"):
            MultiModelDetector()
    
    def test_init_single_model(self):
        """Test initialization with single model"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock_client:
            mock_client.return_value.model_name = "openai"
            detector = MultiModelDetector(openai_api_key="test_key")
            
            assert len(detector.models) == 1
            assert detector.confidence_threshold == 0.7
    
    def test_init_multiple_models(self):
        """Test initialization with multiple models"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock_openai, \
             patch('fakephoto.models.gemini_client.GeminiClient') as mock_gemini, \
             patch('fakephoto.models.anthropic_client.AnthropicClient') as mock_anthropic:
            
            mock_openai.return_value.model_name = "openai"
            mock_gemini.return_value.model_name = "gemini"
            mock_anthropic.return_value.model_name = "anthropic"
            
            detector = MultiModelDetector(
                openai_api_key="test_key",
                google_api_key="test_key",
                anthropic_api_key="test_key"
            )
            
            assert len(detector.models) == 3
    
    def test_init_custom_threshold(self):
        """Test initialization with custom threshold"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock_client:
            mock_client.return_value.model_name = "openai"
            detector = MultiModelDetector(
                openai_api_key="test_key",
                confidence_threshold=0.5
            )
            
            assert detector.confidence_threshold == 0.5


class TestMultiModelDetectorAnalysis:
    """Tests for detector analysis functionality"""
    
    @pytest.fixture
    def mock_detector(self):
        """Create detector with mocked models"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock_client:
            mock_instance = Mock()
            mock_instance.model_name = "openai"
            mock_instance.analyze.return_value = ModelResult(
                model_name="openai",
                ai_probability=0.8,
                confidence=0.9,
                reasoning="Test",
                indicators=["indicator1"]
            )
            mock_client.return_value = mock_instance
            
            detector = MultiModelDetector(openai_api_key="test_key")
            return detector
    
    def test_is_video(self, mock_detector):
        """Test video file detection"""
        assert mock_detector._is_video(Path("test.mp4")) is True
        assert mock_detector._is_video(Path("test.avi")) is True
        assert mock_detector._is_video(Path("test.mov")) is True
        assert mock_detector._is_video(Path("test.jpg")) is False
        assert mock_detector._is_video(Path("test.png")) is False
    
    def test_is_supported_format(self, mock_detector):
        """Test supported format detection"""
        supported = ['.jpg', '.jpeg', '.png', '.webp', '.heic', 
                     '.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        for ext in supported:
            assert mock_detector._is_supported_format(Path(f"test{ext}")) is True
        
        assert mock_detector._is_supported_format(Path("test.txt")) is False
        assert mock_detector._is_supported_format(Path("test.pdf")) is False
    
    def test_analyze_file_not_found(self, mock_detector):
        """Test analysis with non-existent file"""
        with pytest.raises(FileNotFoundError):
            mock_detector.analyze("/nonexistent/file.jpg")
    
    def test_aggregate_results(self, mock_detector):
        """Test result aggregation"""
        model_results = [
            ModelResult("openai", 0.8, 0.9, "Reason 1", ["ind1"]),
            ModelResult("gemini", 0.7, 0.8, "Reason 2", ["ind2"]),
        ]
        
        result = mock_detector._aggregate_results("test.jpg", model_results)
        
        assert isinstance(result, DetectionResult)
        assert result.filename == "test.jpg"
        assert "openai" in result.model_scores
        assert "gemini" in result.model_scores
    
    def test_aggregate_results_empty(self, mock_detector):
        """Test aggregation with empty results"""
        with pytest.raises(ValueError, match="No model results"):
            mock_detector._aggregate_results("test.jpg", [])
    
    def test_consensus_strong(self, mock_detector):
        """Test strong consensus detection"""
        model_results = [
            ModelResult("openai", 0.85, 0.9, "", []),
            ModelResult("gemini", 0.88, 0.85, "", []),
            ModelResult("anthropic", 0.82, 0.9, "", []),
        ]
        
        result = mock_detector._aggregate_results("test.jpg", model_results)
        assert result.consensus == "strong"
        assert result.is_ai_generated is True
    
    def test_consensus_weak(self, mock_detector):
        """Test weak consensus detection"""
        model_results = [
            ModelResult("openai", 0.3, 0.9, "", []),
            ModelResult("gemini", 0.8, 0.85, "", []),
            ModelResult("anthropic", 0.4, 0.9, "", []),
        ]
        
        result = mock_detector._aggregate_results("test.jpg", model_results)
        assert result.consensus == "weak"
    
    def test_consensus_moderate(self, mock_detector):
        """Test moderate consensus detection"""
        model_results = [
            ModelResult("openai", 0.75, 0.9, "", []),
            ModelResult("gemini", 0.8, 0.85, "", []),
        ]
        
        result = mock_detector._aggregate_results("test.jpg", model_results)
        assert result.consensus == "moderate"


class TestGenerateRecommendations:
    """Tests for recommendation generation"""
    
    @pytest.fixture
    def mock_detector(self):
        """Create detector with mocked models"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock_client:
            mock_client.return_value.model_name = "openai"
            detector = MultiModelDetector(openai_api_key="test_key")
            return detector
    
    def test_high_probability_recommendation(self, mock_detector):
        """Test recommendation for high probability"""
        recs = mock_detector._generate_recommendations(0.85, "strong", [])
        
        assert any("High probability" in r for r in recs)
    
    def test_medium_probability_recommendation(self, mock_detector):
        """Test recommendation for medium probability"""
        recs = mock_detector._generate_recommendations(0.6, "moderate", [])
        
        assert any("Possible AI" in r for r in recs)
    
    def test_low_probability_recommendation(self, mock_detector):
        """Test recommendation for low probability"""
        recs = mock_detector._generate_recommendations(0.2, "strong", [])
        
        assert any("Likely authentic" in r for r in recs)
    
    def test_weak_consensus_warning(self, mock_detector):
        """Test warning for weak consensus"""
        recs = mock_detector._generate_recommendations(0.5, "weak", [])
        
        assert any("Low model consensus" in r for r in recs)
    
    def test_multiple_indicators_warning(self, mock_detector):
        """Test warning for many indicators"""
        indicators = ["ind1", "ind2", "ind3", "ind4"]
        recs = mock_detector._generate_recommendations(0.5, "strong", indicators)
        
        assert any("Multiple AI indicators" in r for r in recs)


class TestAnalyzeImageFunction:
    """Tests for the analyze_image convenience function"""
    
    @patch('fakephoto.detector.MultiModelDetector')
    def test_analyze_image(self, mock_detector_class):
        """Test analyze_image convenience function"""
        mock_result = Mock()
        mock_result.filename = "test.jpg"
        mock_detector = Mock()
        mock_detector.analyze.return_value = mock_result
        mock_detector_class.return_value = mock_detector
        
        result = analyze_image(
            "test.jpg",
            openai_key="test",
            google_key="test",
            anthropic_key="test"
        )
        
        assert result.filename == "test.jpg"
        mock_detector.analyze.assert_called_once()


class TestBatchAnalysis:
    """Tests for batch analysis"""
    
    @pytest.fixture
    def mock_detector(self):
        """Create detector with mocked models"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock_client:
            mock_instance = Mock()
            mock_instance.model_name = "openai"
            mock_client.return_value = mock_instance
            
            detector = MultiModelDetector(openai_api_key="test_key")
            return detector
    
    @patch('pathlib.Path.iterdir')
    def test_analyze_batch(self, mock_iterdir, mock_detector):
        """Test batch analysis"""
        mock_files = [
            Path("image1.jpg"),
            Path("image2.png"),
            Path("document.txt"),  # Should be skipped
        ]
        mock_iterdir.return_value = mock_files
        
        with patch.object(mock_detector, 'analyze') as mock_analyze:
            mock_analyze.return_value = DetectionResult(
                filename="test.jpg",
                is_ai_generated=False,
                confidence_score=50.0,
                model_scores={},
                consensus="weak",
                indicators=[],
                recommendations=[]
            )
            
            results = mock_detector.analyze_batch("/fake/dir")
            
            # Only 2 image files should be processed
            assert mock_analyze.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
