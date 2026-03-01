"""
End-to-end integration tests for FakePhoto.ai
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fakephoto import MultiModelDetector, DetectionResult, analyze_image
from fakephoto.detector import ModelResult
from fakephoto.preprocessors.image_processor import ImageProcessor
from fakephoto.preprocessors.video_processor import VideoProcessor
from fakephoto.aggregators.confidence_aggregator import (
    ConfidenceAggregator,
    ConsensusLevel,
    AggregatedResult
)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_image_file(temp_directory):
    """Create a mock image file"""
    img_path = temp_directory / "test_image.jpg"
    # Create a minimal JPEG-like file (not valid JPEG but sufficient for mocking)
    img_path.write_bytes(b"\xff\xd8\xff\xe0fake_jpeg_data\xff\xd9")
    return img_path


@pytest.fixture
def mock_video_file(temp_directory):
    """Create a mock video file path"""
    video_path = temp_directory / "test_video.mp4"
    video_path.write_bytes(b"fake_video_data")
    return video_path


@pytest.fixture
def mock_model_results():
    """Create sample model results for testing"""
    return [
        ModelResult(
            model_name="openai",
            ai_probability=0.85,
            confidence=0.90,
            reasoning="Strong AI indicators detected",
            indicators=["unnatural lighting", "texture artifacts"]
        ),
        ModelResult(
            model_name="gemini",
            ai_probability=0.80,
            confidence=0.85,
            reasoning="AI generation likely",
            indicators=["facial anomalies", "pattern repetition"]
        ),
        ModelResult(
            model_name="anthropic",
            ai_probability=0.75,
            confidence=0.88,
            reasoning="Synthetic appearance detected",
            indicators=["edge artifacts", "noise inconsistencies"]
        ),
    ]


class TestEndToEndDetection:
    """End-to-end tests for the detection pipeline"""
    
    @patch('fakephoto.models.openai_client.OpenAIClient')
    @patch('fakephoto.models.gemini_client.GeminiClient')
    @patch('fakephoto.models.anthropic_client.AnthropicClient')
    def test_full_detection_pipeline(
        self,
        mock_anthropic,
        mock_gemini,
        mock_openai,
        mock_image_file
    ):
        """Test complete detection pipeline with all models"""
        # Setup mock model clients
        mock_openai.return_value.model_name = "openai"
        mock_openai.return_value.analyze.return_value = ModelResult(
            model_name="openai",
            ai_probability=0.85,
            confidence=0.90,
            reasoning="AI detected",
            indicators=["indicator1"]
        )
        
        mock_gemini.return_value.model_name = "gemini"
        mock_gemini.return_value.analyze.return_value = ModelResult(
            model_name="gemini",
            ai_probability=0.80,
            confidence=0.85,
            reasoning="AI likely",
            indicators=["indicator2"]
        )
        
        mock_anthropic.return_value.model_name = "anthropic"
        mock_anthropic.return_value.analyze.return_value = ModelResult(
            model_name="anthropic",
            ai_probability=0.75,
            confidence=0.88,
            reasoning="AI possible",
            indicators=["indicator3"]
        )
        
        # Create detector and analyze
        detector = MultiModelDetector(
            openai_api_key="test_key",
            google_api_key="test_key",
            anthropic_api_key="test_key"
        )
        
        result = detector.analyze(mock_image_file)
        
        # Verify result structure
        assert isinstance(result, DetectionResult)
        assert result.filename == mock_image_file.name
        assert result.is_ai_generated is True
        assert result.confidence_score > 50.0
        assert "openai" in result.model_scores
        assert "gemini" in result.model_scores
        assert "anthropic" in result.model_scores
        assert len(result.indicators) > 0
        assert len(result.recommendations) > 0
    
    @patch('fakephoto.models.openai_client.OpenAIClient')
    def test_single_model_pipeline(self, mock_openai, mock_image_file):
        """Test pipeline with single model"""
        mock_openai.return_value.model_name = "openai"
        mock_openai.return_value.analyze.return_value = ModelResult(
            model_name="openai",
            ai_probability=0.30,
            confidence=0.85,
            reasoning="Likely authentic",
            indicators=[]
        )
        
        detector = MultiModelDetector(openai_api_key="test_key")
        result = detector.analyze(mock_image_file)
        
        assert isinstance(result, DetectionResult)
        assert result.is_ai_generated is False
    
    @patch('fakephoto.models.openai_client.OpenAIClient')
    @patch('fakephoto.preprocessors.video_processor.VideoProcessor')
    def test_video_analysis_pipeline(
        self,
        mock_video_processor_class,
        mock_openai,
        mock_video_file,
        temp_directory
    ):
        """Test video analysis pipeline"""
        # Setup video processor mock
        mock_processor = Mock()
        mock_processor.extract_frames.return_value = [
            temp_directory / "frame_1.jpg",
            temp_directory / "frame_2.jpg"
        ]
        mock_video_processor_class.return_value = mock_processor
        
        # Setup model mock
        mock_openai.return_value.model_name = "openai"
        mock_openai.return_value.analyze.return_value = ModelResult(
            model_name="openai",
            ai_probability=0.70,
            confidence=0.80,
            reasoning="Analysis",
            indicators=["indicator"]
        )
        
        detector = MultiModelDetector(openai_api_key="test_key")
        result = detector.analyze(mock_video_file)
        
        assert isinstance(result, DetectionResult)


class TestConfidenceAggregatorIntegration:
    """Integration tests for confidence aggregation"""
    
    def test_full_aggregation(self, mock_model_results):
        """Test complete aggregation workflow"""
        aggregator = ConfidenceAggregator()
        result = aggregator.aggregate(mock_model_results)
        
        assert isinstance(result, AggregatedResult)
        assert 0.0 <= result.final_probability <= 1.0
        assert 0.0 <= result.confidence_score <= 1.0
        assert isinstance(result.consensus_level, ConsensusLevel)
        assert len(result.contributing_indicators) > 0
        assert len(result.reliability_note) > 0
    
    def test_aggregation_strong_consensus(self):
        """Test aggregation with strong consensus"""
        results = [
            ModelResult("openai", 0.85, 0.9, "", []),
            ModelResult("gemini", 0.87, 0.88, "", []),
            ModelResult("anthropic", 0.84, 0.85, "", []),
        ]
        
        aggregator = ConfidenceAggregator()
        result = aggregator.aggregate(results)
        
        assert result.consensus_level == ConsensusLevel.STRONG
    
    def test_aggregation_conflicting_results(self):
        """Test aggregation with conflicting results"""
        results = [
            ModelResult("openai", 0.90, 0.9, "", []),
            ModelResult("gemini", 0.20, 0.85, "", []),
            ModelResult("anthropic", 0.85, 0.88, "", []),
        ]
        
        aggregator = ConfidenceAggregator()
        result = aggregator.aggregate(results)
        
        assert result.consensus_level in [ConsensusLevel.WEAK, ConsensusLevel.CONFLICTING]
    
    def test_verdict_generation(self):
        """Test verdict generation from aggregated results"""
        aggregator = ConfidenceAggregator()
        
        # High confidence AI
        high_ai = AggregatedResult(
            final_probability=0.85,
            confidence_score=0.85,
            consensus_level=ConsensusLevel.STRONG,
            model_weights={},
            contributing_indicators=[],
            reliability_note=""
        )
        is_ai, verdict = aggregator.get_verdict(high_ai)
        assert is_ai is True
        assert "High confidence" in verdict
        
        # High confidence authentic
        high_auth = AggregatedResult(
            final_probability=0.15,
            confidence_score=0.85,
            consensus_level=ConsensusLevel.STRONG,
            model_weights={},
            contributing_indicators=[],
            reliability_note=""
        )
        is_ai, verdict = aggregator.get_verdict(high_auth)
        assert is_ai is False
        assert "authentic" in verdict.lower()


class TestPreprocessorIntegration:
    """Integration tests for preprocessors"""
    
    def test_image_processor_workflow(self, temp_directory):
        """Test image processor end-to-end"""
        # Create a simple test image
        from PIL import Image
        import numpy as np
        
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_img = Image.fromarray(img_array)
        input_path = temp_directory / "input.jpg"
        test_img.save(input_path)
        
        # Process image
        processor = ImageProcessor(target_size=(512, 512))
        output_path = processor.process(input_path)
        
        assert output_path.exists()
        
        # Verify output
        processed = Image.open(output_path)
        assert processed.size == (512, 512)
        assert processed.mode == "RGB"
    
    def test_image_processor_info_extraction(self, temp_directory):
        """Test image info extraction"""
        from PIL import Image
        import numpy as np
        
        img_array = np.random.randint(0, 255, (200, 100, 3), dtype=np.uint8)
        test_img = Image.fromarray(img_array)
        input_path = temp_directory / "test.jpg"
        test_img.save(input_path)
        
        processor = ImageProcessor()
        info = processor.get_image_info(input_path)
        
        assert info["width"] == 100
        assert info["height"] == 200
        assert info["mode"] == "RGB"
    
    def test_batch_processing(self, temp_directory):
        """Test batch image processing"""
        from PIL import Image
        import numpy as np
        
        # Create test images
        for i in range(3):
            img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            test_img = Image.fromarray(img_array)
            test_img.save(temp_directory / f"test_{i}.jpg")
        
        # Add a non-image file
        (temp_directory / "readme.txt").write_text("test")
        
        processor = ImageProcessor()
        output_dir = temp_directory / "processed"
        results = processor.batch_process(temp_directory, output_dir)
        
        assert len(results) == 3
        for path in results:
            assert path.exists()


class TestBatchAnalysis:
    """Integration tests for batch analysis"""
    
    @patch('fakephoto.models.openai_client.OpenAIClient')
    def test_batch_folder_processing(self, mock_openai, temp_directory):
        """Test batch processing of a folder"""
        # Create test files
        from PIL import Image
        import numpy as np
        
        for i in range(3):
            img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            test_img = Image.fromarray(img_array)
            test_img.save(temp_directory / f"image_{i}.jpg")
        
        mock_openai.return_value.model_name = "openai"
        mock_openai.return_value.analyze.return_value = ModelResult(
            model_name="openai",
            ai_probability=0.75,
            confidence=0.80,
            reasoning="Test",
            indicators=["indicator"]
        )
        
        detector = MultiModelDetector(openai_api_key="test_key")
        results = detector.analyze_batch(temp_directory)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, DetectionResult)


class TestErrorHandling:
    """Integration tests for error handling"""
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file"""
        with patch('fakephoto.models.openai_client.OpenAIClient') as mock:
            mock.return_value.model_name = "openai"
            detector = MultiModelDetector(openai_api_key="test_key")
            
            with pytest.raises(FileNotFoundError):
                detector.analyze("/nonexistent/file.jpg")
    
    @patch('fakephoto.models.openai_client.OpenAIClient')
    def test_model_error_recovery(self, mock_openai, mock_image_file):
        """Test recovery when one model fails"""
        # First model succeeds, second fails
        mock_openai.return_value.model_name = "openai"
        mock_openai.return_value.analyze.side_effect = [
            ModelResult("openai", 0.80, 0.85, "", []),
            Exception("API Error"),
        ]
        
        with patch('fakephoto.models.gemini_client.GeminiClient') as mock_gemini:
            mock_gemini.return_value.model_name = "gemini"
            mock_gemini.return_value.analyze.side_effect = Exception("API Error")
            
            detector = MultiModelDetector(
                openai_api_key="test_key",
                google_api_key="test_key"
            )
            
            # Should still work with one successful model
            result = detector.analyze(mock_image_file)
            assert isinstance(result, DetectionResult)


class TestCLIIntegration:
    """Integration tests for CLI"""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('fakephoto.cli.MultiModelDetector')
    @patch('fakephoto.cli.load_env_file')
    def test_cli_analyze_command(self, mock_load_env, mock_detector_class, temp_directory):
        """Test CLI analyze command"""
        from fakephoto.cli import cmd_analyze
        from argparse import Namespace
        
        # Create test image
        from PIL import Image
        import numpy as np
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_img = Image.fromarray(img_array)
        test_file = temp_directory / "test.jpg"
        test_img.save(test_file)
        
        # Setup mock
        mock_detector = Mock()
        mock_detector.analyze.return_value = DetectionResult(
            filename="test.jpg",
            is_ai_generated=True,
            confidence_score=85.0,
            model_scores={"openai": {"ai_probability": 0.85, "confidence": 0.9}},
            consensus="strong",
            indicators=["indicator1"],
            recommendations=["rec1"]
        )
        mock_detector_class.return_value = mock_detector
        
        args = Namespace(
            file=str(test_file),
            models="openai",
            threshold=0.7,
            output=None,
            verbose=False
        )
        
        result = cmd_analyze(args)
        assert result == 0
        mock_detector.analyze.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
