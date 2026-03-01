"""
FakePhoto.ai - Multi-Model AI Detection Engine
Main detector module
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelResult:
    """Result from a single AI model"""
    model_name: str
    ai_probability: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reasoning: str
    indicators: List[str]


@dataclass
class DetectionResult:
    """Aggregated detection result"""
    filename: str
    is_ai_generated: bool
    confidence_score: float  # 0.0 to 100.0
    model_scores: Dict[str, dict]
    consensus: str  # 'strong', 'moderate', 'weak'
    indicators: List[str]
    recommendations: List[str]


class MultiModelDetector:
    """
    Main detection engine using multiple AI models
    
    Uses OpenAI GPT-4V, Google Gemini, and Anthropic Claude
    to analyze images/videos for AI-generated content.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize the detector
        
        Args:
            openai_api_key: OpenAI API key
            google_api_key: Google API key
            anthropic_api_key: Anthropic API key
            confidence_threshold: Threshold for AI detection (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.models = []
        
        # Initialize model clients
        if openai_api_key:
            from .models.openai_client import OpenAIClient
            self.models.append(OpenAIClient(openai_api_key))
            
        if google_api_key:
            from .models.gemini_client import GeminiClient
            self.models.append(GeminiClient(google_api_key))
            
        if anthropic_api_key:
            from .models.anthropic_client import AnthropicClient
            self.models.append(AnthropicClient(anthropic_api_key))
        
        if not self.models:
            raise ValueError("At least one API key must be provided")
        
        logger.info(f"Initialized detector with {len(self.models)} models")
    
    def analyze(self, file_path: Union[str, Path]) -> DetectionResult:
        """
        Analyze an image or video file
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            DetectionResult with aggregated analysis
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Analyzing {file_path}")
        
        # Preprocess based on file type
        if self._is_video(file_path):
            frames = self._extract_frames(file_path)
        else:
            frames = [file_path]
        
        # Get results from all models
        model_results = []
        for model in self.models:
            try:
                result = model.analyze(frames)
                model_results.append(result)
            except Exception as e:
                logger.error(f"Error with {model.__class__.__name__}: {e}")
        
        # Aggregate results
        return self._aggregate_results(file_path.name, model_results)
    
    def analyze_batch(self, folder_path: Union[str, Path]) -> List[DetectionResult]:
        """
        Analyze all images/videos in a folder
        
        Args:
            folder_path: Path to folder containing files
            
        Returns:
            List of DetectionResult for each file
        """
        folder_path = Path(folder_path)
        results = []
        
        for file_path in folder_path.iterdir():
            if self._is_supported_format(file_path):
                try:
                    result = self.analyze(file_path)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _is_video(self, file_path: Path) -> bool:
        """Check if file is a video"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        return file_path.suffix.lower() in video_extensions
    
    def _is_supported_format(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        supported = {'.jpg', '.jpeg', '.png', '.webp', '.heic', 
                     '.mp4', '.avi', '.mov', '.mkv', '.webm'}
        return file_path.suffix.lower() in supported
    
    def _extract_frames(self, video_path: Path, num_frames: int = 5) -> List[Path]:
        """
        Extract frames from video for analysis
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            
        Returns:
            List of frame paths
        """
        # TODO: Implement frame extraction using OpenCV
        logger.info(f"Extracting {num_frames} frames from {video_path}")
        return []
    
    def _aggregate_results(
        self, 
        filename: str, 
        model_results: List[ModelResult]
    ) -> DetectionResult:
        """
        Aggregate results from multiple models
        
        Uses weighted voting based on model confidence
        """
        if not model_results:
            raise ValueError("No model results to aggregate")
        
        # Calculate weighted average
        total_weight = sum(r.confidence for r in model_results)
        weighted_probability = sum(
            r.ai_probability * r.confidence for r in model_results
        ) / total_weight
        
        # Determine consensus
        high_confidence_votes = sum(
            1 for r in model_results 
            if r.ai_probability > self.confidence_threshold
        )
        
        if high_confidence_votes == len(model_results):
            consensus = 'strong'
        elif high_confidence_votes > len(model_results) / 2:
            consensus = 'moderate'
        else:
            consensus = 'weak'
        
        # Collect unique indicators
        all_indicators = set()
        for result in model_results:
            all_indicators.update(result.indicators)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            weighted_probability, 
            consensus,
            list(all_indicators)
        )
        
        return DetectionResult(
            filename=filename,
            is_ai_generated=weighted_probability > self.confidence_threshold,
            confidence_score=weighted_probability * 100,
            model_scores={
                r.model_name: {
                    'ai_probability': r.ai_probability,
                    'confidence': r.confidence
                } for r in model_results
            },
            consensus=consensus,
            indicators=list(all_indicators),
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self, 
        probability: float, 
        consensus: str,
        indicators: List[str]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if probability > 0.8:
            recommendations.append(
                "High probability of AI generation. Verify with additional tools."
            )
        elif probability > 0.5:
            recommendations.append(
                "Possible AI generation. Manual review recommended."
            )
        else:
            recommendations.append(
                "Likely authentic, but verify source credibility."
            )
        
        if consensus == 'weak':
            recommendations.append(
                "Low model consensus - results may be unreliable."
            )
        
        if len(indicators) > 3:
            recommendations.append(
                "Multiple AI indicators detected - high scrutiny warranted."
            )
        
        return recommendations


# Convenience function
def analyze_image(
    file_path: str,
    openai_key: Optional[str] = None,
    google_key: Optional[str] = None,
    anthropic_key: Optional[str] = None
) -> DetectionResult:
    """
    Quick analysis function
    
    Args:
        file_path: Path to image/video
        openai_key: OpenAI API key
        google_key: Google API key  
        anthropic_key: Anthropic API key
        
    Returns:
        DetectionResult
    """
    detector = MultiModelDetector(
        openai_api_key=openai_key,
        google_api_key=google_key,
        anthropic_api_key=anthropic_key
    )
    return detector.analyze(file_path)
