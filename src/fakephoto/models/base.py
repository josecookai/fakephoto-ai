"""
Base model client interface
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path


class BaseModelClient(ABC):
    """Abstract base class for AI model clients"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "base"
    
    @abstractmethod
    def analyze(self, frames: List[Path]) -> "ModelResult":
        """
        Analyze frames and return result
        
        Args:
            frames: List of image file paths
            
        Returns:
            ModelResult
        """
        pass
