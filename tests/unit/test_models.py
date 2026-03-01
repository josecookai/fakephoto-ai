"""
Unit tests for model clients
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import base64
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fakephoto.models.base import BaseModelClient
from fakephoto.models.openai_client import OpenAIClient
from fakephoto.models.gemini_client import GeminiClient
from fakephoto.models.anthropic_client import AnthropicClient
from fakephoto.detector import ModelResult


class TestBaseModelClient:
    """Tests for the base model client"""
    
    def test_base_client_init(self):
        """Test base client initialization"""
        
        class TestClient(BaseModelClient):
            def analyze(self, frames):
                pass
        
        client = TestClient("test_api_key")
        assert client.api_key == "test_api_key"
        assert client.model_name == "base"
    
    def test_base_client_abstract(self):
        """Test that base client cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseModelClient("test_key")


class TestOpenAIClient:
    """Tests for OpenAI client"""
    
    @pytest.fixture
    def mock_openai(self):
        """Create mock OpenAI client"""
        with patch('fakephoto.models.openai_client.OpenAI') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock, mock_instance
    
    def test_init(self, mock_openai):
        """Test OpenAI client initialization"""
        mock_class, _ = mock_openai
        client = OpenAIClient("test_key")
        
        assert client.model_name == "openai"
        assert client.api_key == "test_key"
        mock_class.assert_called_once_with(api_key="test_key")
    
    def test_init_import_error(self):
        """Test handling of missing openai package"""
        with patch.dict('sys.modules', {'openai': None}):
            with pytest.raises(ImportError, match="Install openai"):
                OpenAIClient("test_key")
    
    def test_analyze(self, mock_openai, tmp_path):
        """Test image analysis"""
        _, mock_instance = mock_openai
        
        # Create a test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake_image_data")
        
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        This image appears to be AI-generated.
        AI Probability: 0.85
        Indicators: Unnatural lighting, texture issues
        """
        mock_instance.chat.completions.create.return_value = mock_response
        
        client = OpenAIClient("test_key")
        
        with patch('builtins.open', mock_open(read_data=b"fake_image_data")):
            with patch.object(client, '_extract_probability', return_value=0.85):
                with patch.object(client, '_extract_indicators', return_value=["indicator1"]):
                    result = client.analyze([test_image])
        
        assert isinstance(result, ModelResult)
        assert result.model_name == "openai"
    
    def test_extract_probability(self, mock_openai):
        """Test probability extraction"""
        client = OpenAIClient("test_key")
        
        assert client._extract_probability("likely ai-generated") == 0.8
        assert client._extract_probability("possibly ai") == 0.5
        assert client._extract_probability("authentic and real") == 0.2
        assert client._extract_probability("unclear") == 0.5
    
    def test_extract_indicators(self, mock_openai):
        """Test indicator extraction"""
        client = OpenAIClient("test_key")
        
        indicators = client._extract_indicators(
            "The image has unnatural lighting, texture problems, and facial anomalies"
        )
        
        assert "Unnatural lighting" in indicators
        assert "Texture inconsistencies" in indicators
        assert "Facial anomalies" in indicators
    
    def test_analyze_api_error(self, mock_openai, tmp_path):
        """Test handling of API errors"""
        _, mock_instance = mock_openai
        mock_instance.chat.completions.create.side_effect = Exception("API Error")
        
        client = OpenAIClient("test_key")
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake_image_data")
        
        with pytest.raises(RuntimeError, match="OpenAI API error"):
            client.analyze([test_image])


class TestGeminiClient:
    """Tests for Gemini client"""
    
    @pytest.fixture
    def mock_genai(self):
        """Create mock Gemini client"""
        with patch('fakephoto.models.gemini_client.google.generativeai') as mock:
            mock_model = Mock()
            mock.configure = Mock()
            mock.GenerativeModel.return_value = mock_model
            yield mock, mock_model
    
    def test_init(self, mock_genai):
        """Test Gemini client initialization"""
        mock_module, _ = mock_genai
        client = GeminiClient("test_key")
        
        assert client.model_name == "gemini"
        mock_module.configure.assert_called_once_with(api_key="test_key")
    
    def test_init_import_error(self):
        """Test handling of missing google-generativeai package"""
        with patch.dict('sys.modules', {'google.generativeai': None}):
            with pytest.raises(ImportError, match="google-generativeai"):
                GeminiClient("test_key")
    
    def test_analyze(self, mock_genai, tmp_path):
        """Test image analysis"""
        _, mock_model = mock_genai
        
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake_image_data")
        
        # Mock response
        mock_response = Mock()
        mock_response.text = """
        AI Probability: 0.75
        Confidence: 0.85
        Indicators: lighting issues, texture problems
        Reasoning: Test reasoning
        """
        mock_model.generate_content.return_value = mock_response
        
        client = GeminiClient("test_key")
        
        with patch.object(client, '_extract_probability', return_value=0.75):
            with patch.object(client, '_extract_confidence', return_value=0.85):
                with patch.object(client, '_extract_indicators', return_value=["indicator"]):
                    result = client.analyze([test_image])
        
        assert isinstance(result, ModelResult)
        assert result.model_name == "gemini"
    
    def test_extract_probability(self, mock_genai):
        """Test probability extraction"""
        client = GeminiClient("test_key")
        
        # Test explicit extraction
        assert client._extract_probability("AI Probability: 0.85") == 0.85
        assert client._extract_probability("AI Probability: 85%") == 0.85
        
        # Test keyword fallback
        assert client._extract_probability("definitely ai") == 0.95
        assert client._extract_probability("likely ai") == 0.75
        assert client._extract_probability("authentic photo") == 0.15
    
    def test_extract_confidence(self, mock_genai):
        """Test confidence extraction"""
        client = GeminiClient("test_key")
        
        assert client._extract_confidence("Confidence: 0.90") == 0.90
        assert client._extract_confidence("No confidence info") == 0.70  # Default
    
    def test_get_image_format(self, mock_genai):
        """Test image format detection"""
        client = GeminiClient("test_key")
        
        assert client._get_image_format(Path("test.jpg")) == "jpeg"
        assert client._get_image_format(Path("test.png")) == "png"
        assert client._get_image_format(Path("test.webp")) == "webp"
    
    def test_analyze_empty_frames(self, mock_genai):
        """Test analysis with empty frames"""
        client = GeminiClient("test_key")
        
        with pytest.raises(ValueError, match="No frames provided"):
            client.analyze([])


class TestAnthropicClient:
    """Tests for Anthropic client"""
    
    @pytest.fixture
    def mock_anthropic(self):
        """Create mock Anthropic client"""
        with patch('fakephoto.models.anthropic_client.anthropic') as mock:
            mock_client = Mock()
            mock.Anthropic.return_value = mock_client
            yield mock, mock_client
    
    def test_init(self, mock_anthropic):
        """Test Anthropic client initialization"""
        mock_module, _ = mock_anthropic
        client = AnthropicClient("test_key")
        
        assert client.model_name == "anthropic"
    
    def test_init_import_error(self):
        """Test handling of missing anthropic package"""
        with patch.dict('sys.modules', {'anthropic': None}):
            with pytest.raises(ImportError, match="anthropic"):
                AnthropicClient("test_key")
    
    def test_analyze(self, mock_anthropic, tmp_path):
        """Test image analysis"""
        _, mock_client = mock_anthropic
        
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake_image_data")
        
        # Mock response
        mock_response = Mock()
        mock_message = Mock()
        mock_message.text = """
        AI Probability: 0.70
        Confidence: 0.80
        Key Indicators: texture issues
        Detailed Reasoning: Test reasoning
        """
        mock_response.content = [mock_message]
        mock_client.messages.create.return_value = mock_response
        
        client = AnthropicClient("test_key")
        
        with patch.object(client, '_extract_probability', return_value=0.70):
            with patch.object(client, '_extract_confidence', return_value=0.80):
                with patch.object(client, '_extract_indicators', return_value=["indicator"]):
                    result = client.analyze([test_image])
        
        assert isinstance(result, ModelResult)
        assert result.model_name == "anthropic"
    
    def test_get_media_type(self, mock_anthropic):
        """Test media type detection"""
        client = AnthropicClient("test_key")
        
        assert client._get_media_type(Path("test.jpg")) == "image/jpeg"
        assert client._get_media_type(Path("test.png")) == "image/png"
        assert client._get_media_type(Path("test.webp")) == "image/webp"
    
    def test_extract_probability(self, mock_anthropic):
        """Test probability extraction"""
        client = AnthropicClient("test_key")
        
        # Test explicit extraction
        assert client._extract_probability("AI Probability: 0.65") == 0.65
        
        # Test keyword fallback
        assert client._extract_probability("almost certainly ai") == 0.95
        assert client._extract_probability("highly likely authentic") == 0.15
    
    def test_extract_confidence(self, mock_anthropic):
        """Test confidence extraction"""
        client = AnthropicClient("test_key")
        
        # Test explicit
        assert client._extract_confidence("Confidence: 0.85") == 0.85
        
        # Test signal-based
        high_conf = client._extract_confidence("This is certainly and definitely clear")
        assert high_conf > 0.75
        
        low_conf = client._extract_confidence("This is uncertain and ambiguous")
        assert low_conf < 0.75
    
    def test_extract_indicators(self, mock_anthropic):
        """Test indicator extraction"""
        client = AnthropicClient("test_key")
        
        text = """
        The image shows texture irregularities, anatomical inconsistencies,
        lighting issues, and generation artifacts.
        """
        indicators = client._extract_indicators(text)
        
        assert "Texture irregularities" in indicators
        assert "Anatomical inconsistencies" in indicators
        assert "Lighting inconsistencies" in indicators
        assert "Generation artifacts" in indicators


class TestModelResultIntegration:
    """Integration-style tests for model clients"""
    
    def test_model_result_dataclass(self):
        """Test ModelResult can be created and accessed"""
        result = ModelResult(
            model_name="test",
            ai_probability=0.75,
            confidence=0.85,
            reasoning="Test reasoning",
            indicators=["ind1", "ind2"]
        )
        
        # Verify all fields
        assert result.model_name == "test"
        assert result.ai_probability == 0.75
        assert result.confidence == 0.85
        assert result.reasoning == "Test reasoning"
        assert len(result.indicators) == 2
    
    def test_probability_bounds(self):
        """Test that probability values are valid"""
        result = ModelResult(
            model_name="test",
            ai_probability=0.5,
            confidence=0.5,
            reasoning="test",
            indicators=[]
        )
        
        assert 0.0 <= result.ai_probability <= 1.0
        assert 0.0 <= result.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
