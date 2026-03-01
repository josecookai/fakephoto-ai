"""
Anthropic Claude Vision Client
"""

from typing import List
from pathlib import Path
import base64

from .base import BaseModelClient


class AnthropicClient(BaseModelClient):
    """Anthropic Claude Vision API client"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.model_name = "anthropic"
        try:
            import anthropic
            self.anthropic = anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")
    
    def analyze(self, frames: List[Path]) -> "ModelResult":
        """
        Analyze frames using Anthropic Claude Vision
        
        Args:
            frames: List of image paths
            
        Returns:
            ModelResult with analysis
        """
        from ..detector import ModelResult
        
        if not frames:
            raise ValueError("No frames provided for analysis")
        
        # Encode first frame as base64
        frame_path = frames[0]
        with open(frame_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine media type
        media_type = self._get_media_type(frame_path)
        
        # Claude prompt
        prompt = """Analyze this image and determine if it's AI-generated or authentic.

Focus on these aspects:
1. Visual coherence and consistency
2. Natural vs synthetic textures
3. Anatomical correctness (if people present)
4. Lighting and shadow realism
5. Fine detail authenticity
6. Evidence of diffusion model artifacts
7. Metadata and EXIF data (if mentioned)

Provide your analysis in this format:
- AI Probability: [0.0 to 1.0]
- Confidence: [0.0 to 1.0]  
- Key Indicators: [list specific findings]
- Detailed Reasoning: [explanation of analysis]

Be thorough and specific in your observations."""
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Extract metrics
            ai_probability = self._extract_probability(content)
            confidence = self._extract_confidence(content)
            indicators = self._extract_indicators(content)
            
            return ModelResult(
                model_name=self.model_name,
                ai_probability=ai_probability,
                confidence=confidence,
                reasoning=content,
                indicators=indicators
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
    
    def _get_media_type(self, path: Path) -> str:
        """Get media type for Claude API"""
        ext = path.suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        return mime_map.get(ext, 'image/jpeg')
    
    def _extract_probability(self, text: str) -> float:
        """Extract AI probability from response text"""
        import re
        
        patterns = [
            r'AI Probability[:\s]+(\d*\.?\d+)',
            r'probability of being AI[:\s]+(\d*\.?\d+)',
            r'(?:ai|artificial intelligence)[-\s]generated[:\s]+(\d*\.?\d+)',
            r'(\d*\.?\d+)\s*(?:%|percent)',
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
        
        # Keyword-based fallback
        text_lower = text.lower()
        certainty_map = {
            ("almost certainly ai", "definitely ai-generated"): 0.95,
            ("highly likely ai", "strong indicators of ai"): 0.80,
            ("likely ai-generated", "appears to be ai"): 0.65,
            ("possibly ai", "suggestive of ai"): 0.50,
            ("unclear", "ambiguous", "inconclusive"): 0.50,
            ("likely authentic", "appears genuine"): 0.25,
            ("highly likely authentic", "strong evidence of authenticity"): 0.15,
            ("definitely authentic", "certainly genuine"): 0.05
        }
        
        for keywords, prob in certainty_map.items():
            if any(kw in text_lower for kw in keywords):
                return prob
        
        return 0.5
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence level from response text"""
        import re
        
        patterns = [
            r'Confidence[:\s]+(\d*\.?\d+)',
            r'confidence level[:\s]+(\d*\.?\d+)',
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
        
        # Estimate confidence from response characteristics
        confidence_signals = [
            "certainly", "definitely", "clearly", "obviously",
            "strong evidence", "conclusive", "unmistakable"
        ]
        uncertainty_signals = [
            "uncertain", "unclear", "ambiguous", "difficult to determine",
            "inconclusive", "cannot definitively", "limited by"
        ]
        
        text_lower = text.lower()
        conf_count = sum(1 for sig in confidence_signals if sig in text_lower)
        unc_count = sum(1 for sig in uncertainty_signals if sig in text_lower)
        
        base_confidence = 0.75
        if conf_count > unc_count:
            base_confidence = min(0.95, base_confidence + 0.1 * conf_count)
        elif unc_count > conf_count:
            base_confidence = max(0.50, base_confidence - 0.1 * unc_count)
        
        return base_confidence
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract indicators from response text"""
        indicators = []
        text_lower = text.lower()
        
        indicator_map = {
            # Texture and detail
            "texture": "Texture irregularities",
            "overly smooth": "Overly smooth surfaces",
            "unnatural smoothness": "Synthetic smoothness",
            "plastic-like": "Plastic-like appearance",
            "waxy": "Waxy texture",
            
            # Anatomical
            "anatomical": "Anatomical inconsistencies",
            "hand": "Hand structure issues",
            "finger": "Finger anomalies",
            "limb": "Limb proportion issues",
            "facial asymmetry": "Facial asymmetry",
            "eye asymmetry": "Eye asymmetry",
            "unnatural pose": "Unnatural posing",
            
            # Lighting
            "lighting": "Lighting inconsistencies",
            "shadow": "Shadow anomalies",
            "inconsistent light": "Inconsistent light sources",
            "flat lighting": "Flat/unrealistic lighting",
            
            # Artifacts
            "artifact": "Generation artifacts",
            "distortion": "Spatial distortions",
            "blur inconsistency": "Inconsistent blur",
            "repetitive pattern": "Repetitive patterns",
            "watermark-like": "Watermark-like artifacts",
            "grid pattern": "Grid-like patterns",
            
            # Color and composition
            "color": "Color inconsistencies",
            "oversaturated": "Oversaturated colors",
            "unnatural color": "Unnatural coloration",
            "composition": "Composition anomalies",
            "background blur": "Unnatural background blur",
            "depth": "Depth inconsistencies",
            
            # Metadata
            "metadata": "Metadata issues",
            "exif": "EXIF anomalies",
            "no metadata": "Missing metadata"
        }
        
        for keyword, indicator in indicator_map.items():
            if keyword in text_lower:
                indicators.append(indicator)
        
        # Remove duplicates
        seen = set()
        return [x for x in indicators if not (x in seen or seen.add(x))]
