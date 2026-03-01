"""
Google Gemini Vision Client
"""

from typing import List
from pathlib import Path
import base64

from .base import BaseModelClient


class GeminiClient(BaseModelClient):
    """Google Gemini Vision API client"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.model_name = "gemini"
        try:
            import google.generativeai as genai
            self.genai = genai
            self.genai.configure(api_key=api_key)
            # Use the latest Gemini Pro Vision model
            self.model = self.genai.GenerativeModel('gemini-1.5-flash')
        except ImportError:
            raise ImportError("Install google-generativeai: pip install google-generativeai")
    
    def analyze(self, frames: List[Path]) -> "ModelResult":
        """
        Analyze frames using Google Gemini Vision
        
        Args:
            frames: List of image paths
            
        Returns:
            ModelResult with analysis
        """
        from ..detector import ModelResult
        
        if not frames:
            raise ValueError("No frames provided for analysis")
        
        # Load the first frame
        frame_path = frames[0]
        with open(frame_path, "rb") as f:
            image_data = f.read()
        
        # Gemini prompt
        prompt = """
        Analyze this image and determine if it's AI-generated or authentic.
        
        Look for these specific indicators of AI generation:
        1. Unnatural lighting patterns or inconsistent shadows
        2. Texture inconsistencies, especially in skin, hair, or fabrics
        3. Anatomical anomalies (hands, faces, eyes)
        4. Metadata inconsistencies or lack thereof
        5. Repetitive patterns or artifacts typical of GANs
        6. Overly smooth or perfect textures
        7. Strange edge artifacts
        
        Provide your analysis in this format:
        - AI Probability: [0.0 to 1.0]
        - Confidence: [0.0 to 1.0]
        - Indicators: [list specific findings]
        - Reasoning: [brief explanation]
        """
        
        try:
            # Create image part for Gemini
            image_parts = [
                {
                    "mime_type": f"image/{self._get_image_format(frame_path)}",
                    "data": image_data
                }
            ]
            
            # Generate response
            response = self.model.generate_content([prompt, *image_parts])
            response_text = response.text
            
            # Extract metrics from response
            ai_probability = self._extract_probability(response_text)
            confidence = self._extract_confidence(response_text)
            indicators = self._extract_indicators(response_text)
            
            return ModelResult(
                model_name=self.model_name,
                ai_probability=ai_probability,
                confidence=confidence,
                reasoning=response_text,
                indicators=indicators
            )
            
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    def _get_image_format(self, path: Path) -> str:
        """Get image format for mime type"""
        ext = path.suffix.lower()
        format_map = {
            '.jpg': 'jpeg',
            '.jpeg': 'jpeg',
            '.png': 'png',
            '.webp': 'webp',
            '.heic': 'heic'
        }
        return format_map.get(ext, 'jpeg')
    
    def _extract_probability(self, text: str) -> float:
        """Extract AI probability from response text"""
        import re
        
        # Look for explicit probability
        patterns = [
            r'AI Probability[:\s]+(\d*\.?\d+)',
            r'probability[:\s]+(\d*\.?\d+)',
            r'(\d*\.?\d+)\s*probability',
            r'(?:likely|probability)[:\s]+(\d*\.?\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Normalize if given as percentage
                    if value > 1:
                        value = value / 100.0
                    return max(0.0, min(1.0, value))
                except ValueError:
                    continue
        
        # Fallback to keyword analysis
        text_lower = text.lower()
        if "definitely ai" in text_lower or "certainly ai" in text_lower:
            return 0.95
        elif "likely ai" in text_lower or "probably ai" in text_lower:
            return 0.75
        elif "possibly ai" in text_lower or "maybe ai" in text_lower:
            return 0.5
        elif "unlikely ai" in text_lower or "probably not ai" in text_lower:
            return 0.25
        elif "definitely not ai" in text_lower or "certainly authentic" in text_lower:
            return 0.05
        elif "authentic" in text_lower or "real" in text_lower:
            return 0.15
        
        return 0.5  # Default uncertainty
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence level from response text"""
        import re
        
        patterns = [
            r'Confidence[:\s]+(\d*\.?\d+)',
            r'confidence[:\s]+(\d*\.?\d+)',
            r'(\d*\.?\d+)\s*confidence',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    if value > 1:
                        value = value / 100.0
                    return max(0.0, min(1.0, value))
                except ValueError:
                    continue
        
        # Default confidence based on analysis length
        return 0.85 if len(text) > 200 else 0.70
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract indicators from response text"""
        indicators = []
        text_lower = text.lower()
        
        indicator_keywords = {
            "lighting": "Unnatural lighting patterns",
            "shadow": "Inconsistent shadows",
            "texture": "Texture inconsistencies",
            "skin": "Skin texture anomalies",
            "hair": "Hair detail inconsistencies",
            "hand": "Anatomical issues (hands)",
            "finger": "Anatomical issues (fingers)",
            "face": "Facial feature anomalies",
            "eye": "Eye detail issues",
            "metadata": "Metadata anomalies",
            "pattern": "Repetitive patterns",
            "artifact": "AI generation artifacts",
            "edge": "Edge artifacts",
            "smooth": "Overly smooth textures",
            "perfect": "Unnaturally perfect details",
            "distortion": "Spatial distortions",
            "blur": "Inconsistent blur patterns",
            "noise": "Noise pattern inconsistencies",
            "compression": "Compression artifacts",
            "color": "Color inconsistencies"
        }
        
        for keyword, indicator in indicator_keywords.items():
            if keyword in text_lower:
                indicators.append(indicator)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_indicators = []
        for ind in indicators:
            if ind not in seen:
                seen.add(ind)
                unique_indicators.append(ind)
        
        return unique_indicators
