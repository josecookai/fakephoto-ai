"""
OpenAI GPT-4 Vision Client
"""

from typing import List
from pathlib import Path
import base64

from .base import BaseModelClient


class OpenAIClient(BaseModelClient):
    """OpenAI GPT-4 Vision API client"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.model_name = "openai"
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("Install openai: pip install openai")
    
    def analyze(self, frames: List[Path]) -> "ModelResult":
        """
        Analyze frames using GPT-4 Vision
        
        Args:
            frames: List of image paths
            
        Returns:
            ModelResult with analysis
        """
        from ..detector import ModelResult
        
        # Encode first frame
        with open(frames[0], "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        
        # GPT-4 Vision prompt
        prompt = """
        Analyze this image and determine if it's AI-generated or authentic.
        
        Look for:
        1. Unnatural lighting or shadows
        2. Inconsistent textures
        3. Strange facial features (if people present)
        4. Metadata anomalies
        5. Compression artifacts typical of AI
        
        Provide:
        - AI probability (0.0 to 1.0)
        - Confidence level (0.0 to 1.0)
        - Specific indicators found
        - Brief reasoning
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Parse response (simplified)
            content = response.choices[0].message.content
            
            # Extract probability from response
            # In real implementation, use structured output
            ai_probability = self._extract_probability(content)
            
            return ModelResult(
                model_name=self.model_name,
                ai_probability=ai_probability,
                confidence=0.85,  # GPT-4V is generally confident
                reasoning=content,
                indicators=self._extract_indicators(content)
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def _extract_probability(self, text: str) -> float:
        """Extract AI probability from response text"""
        # Simplified extraction
        # Real implementation would use structured JSON output
        text_lower = text.lower()
        if "likely ai" in text_lower or "ai-generated" in text_lower:
            return 0.8
        elif "possibly ai" in text_lower:
            return 0.5
        elif "authentic" in text_lower or "real" in text_lower:
            return 0.2
        return 0.5
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract indicators from response"""
        indicators = []
        text_lower = text.lower()
        
        if "lighting" in text_lower:
            indicators.append("Unnatural lighting")
        if "texture" in text_lower:
            indicators.append("Texture inconsistencies")
        if "face" in text_lower:
            indicators.append("Facial anomalies")
        if "artifact" in text_lower:
            indicators.append("AI artifacts")
        
        return indicators
