"""
Confidence Aggregator - Combine results from multiple models
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConsensusLevel(Enum):
    """Consensus levels from multiple models"""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    CONFLICTING = "conflicting"


@dataclass
class AggregatedResult:
    """Result from confidence aggregation"""
    final_probability: float
    confidence_score: float
    consensus_level: ConsensusLevel
    model_weights: Dict[str, float]
    contributing_indicators: List[str]
    reliability_note: str


class ConfidenceAggregator:
    """
    Aggregate confidence scores from multiple AI models
    
    Uses weighted voting and statistical methods to combine
    model outputs into a unified decision.
    """
    
    # Default model weights based on historical accuracy
    DEFAULT_MODEL_WEIGHTS = {
        "openai": 0.35,
        "gemini": 0.35,
        "anthropic": 0.30
    }
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.5
    AGREEMENT_THRESHOLD = 0.2  # Max difference for consensus
    
    def __init__(
        self,
        model_weights: Optional[Dict[str, float]] = None,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize the aggregator
        
        Args:
            model_weights: Custom weights for each model
            confidence_threshold: Threshold for AI detection
        """
        self.model_weights = model_weights or self.DEFAULT_MODEL_WEIGHTS
        self.confidence_threshold = confidence_threshold
        
        # Normalize weights
        total = sum(self.model_weights.values())
        self.model_weights = {
            k: v / total for k, v in self.model_weights.items()
        }
    
    def aggregate(
        self,
        model_results: List["ModelResult"]
    ) -> AggregatedResult:
        """
        Aggregate results from multiple models
        
        Args:
            model_results: List of ModelResult objects
            
        Returns:
            AggregatedResult with combined analysis
        """
        if not model_results:
            raise ValueError("No model results to aggregate")
        
        # Calculate weighted probability
        weighted_prob = self._calculate_weighted_probability(model_results)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(model_results)
        
        # Determine consensus level
        consensus = self._determine_consensus(model_results)
        
        # Aggregate indicators
        indicators = self._aggregate_indicators(model_results)
        
        # Calculate per-model effective weights
        effective_weights = self._calculate_effective_weights(model_results)
        
        # Generate reliability note
        reliability_note = self._generate_reliability_note(
            weighted_prob, overall_confidence, consensus, model_results
        )
        
        return AggregatedResult(
            final_probability=weighted_prob,
            confidence_score=overall_confidence,
            consensus_level=consensus,
            model_weights=effective_weights,
            contributing_indicators=indicators,
            reliability_note=reliability_note
        )
    
    def _calculate_weighted_probability(
        self,
        results: List["ModelResult"]
    ) -> float:
        """Calculate weighted average probability"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result in results:
            base_weight = self.model_weights.get(result.model_name, 0.33)
            # Adjust weight by model's confidence
            adjusted_weight = base_weight * result.confidence
            
            weighted_sum += result.ai_probability * adjusted_weight
            total_weight += adjusted_weight
        
        if total_weight == 0:
            return 0.5
        
        return weighted_sum / total_weight
    
    def _calculate_overall_confidence(
        self,
        results: List["ModelResult"]
    ) -> float:
        """Calculate overall confidence score"""
        if not results:
            return 0.0
        
        # Average confidence of models
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        # Agreement factor - how much models agree
        probabilities = [r.ai_probability for r in results]
        if len(probabilities) > 1:
            agreement = 1.0 - (max(probabilities) - min(probabilities))
        else:
            agreement = 1.0
        
        # Combine: high agreement boosts confidence
        overall = avg_confidence * (0.7 + 0.3 * agreement)
        
        return min(1.0, overall)
    
    def _determine_consensus(
        self,
        results: List["ModelResult"]
    ) -> ConsensusLevel:
        """Determine the level of consensus among models"""
        if len(results) < 2:
            return ConsensusLevel.MODERATE
        
        probabilities = [r.ai_probability for r in results]
        above_threshold = sum(
            1 for p in probabilities 
            if p > self.confidence_threshold
        )
        
        # Check for strong agreement
        range_prob = max(probabilities) - min(probabilities)
        
        if range_prob < self.AGREEMENT_THRESHOLD:
            # Models agree closely
            if above_threshold == len(results) or above_threshold == 0:
                return ConsensusLevel.STRONG
            else:
                return ConsensusLevel.MODERATE
        elif range_prob < self.AGREEMENT_THRESHOLD * 2:
            # Models somewhat agree
            if above_threshold > len(results) / 2:
                return ConsensusLevel.MODERATE
            else:
                return ConsensusLevel.WEAK
        else:
            # Models disagree significantly
            if above_threshold > 0 and above_threshold < len(results):
                return ConsensusLevel.CONFLICTING
            else:
                return ConsensusLevel.WEAK
    
    def _aggregate_indicators(
        self,
        results: List["ModelResult"]
    ) -> List[str]:
        """Aggregate and rank indicators from all models"""
        from collections import Counter
        
        # Count indicator occurrences
        indicator_counts = Counter()
        indicator_sources = {}
        
        for result in results:
            for indicator in result.indicators:
                indicator_counts[indicator] += 1
                if indicator not in indicator_sources:
                    indicator_sources[indicator] = []
                indicator_sources[indicator].append(result.model_name)
        
        # Score indicators by: mentions * avg confidence of sources
        scored_indicators = []
        for indicator, count in indicator_counts.items():
            source_confidences = [
                r.confidence for r in results 
                if r.model_name in indicator_sources[indicator]
            ]
            avg_conf = sum(source_confidences) / len(source_confidences) if source_confidences else 0
            score = count * avg_conf
            scored_indicators.append((indicator, score, count))
        
        # Sort by score
        scored_indicators.sort(key=lambda x: x[1], reverse=True)
        
        # Return top indicators
        return [ind[0] for ind in scored_indicators[:10]]
    
    def _calculate_effective_weights(
        self,
        results: List["ModelResult"]
    ) -> Dict[str, float]:
        """Calculate effective weights used in aggregation"""
        effective = {}
        total = 0.0
        
        for result in results:
            base = self.model_weights.get(result.model_name, 0.33)
            adjusted = base * result.confidence
            effective[result.model_name] = adjusted
            total += adjusted
        
        # Normalize
        if total > 0:
            effective = {k: v / total for k, v in effective.items()}
        
        return effective
    
    def _generate_reliability_note(
        self,
        probability: float,
        confidence: float,
        consensus: ConsensusLevel,
        results: List["ModelResult"]
    ) -> str:
        """Generate a human-readable reliability note"""
        notes = []
        
        # Confidence-based note
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            notes.append("High confidence assessment")
        elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            notes.append("Moderate confidence assessment")
        else:
            notes.append("Low confidence - results may be unreliable")
        
        # Consensus-based note
        if consensus == ConsensusLevel.STRONG:
            notes.append("Strong model consensus")
        elif consensus == ConsensusLevel.MODERATE:
            notes.append("Moderate model consensus")
        elif consensus == ConsensusLevel.CONFLICTING:
            notes.append("Models show conflicting signals - manual review recommended")
        else:
            notes.append("Weak model consensus")
        
        # Number of models
        if len(results) == 1:
            notes.append("Based on single model analysis")
        elif len(results) == 2:
            notes.append("Based on two models")
        else:
            notes.append(f"Based on {len(results)} models")
        
        return "; ".join(notes)
    
    def get_verdict(
        self,
        aggregated: AggregatedResult
    ) -> Tuple[bool, str]:
        """
        Get final verdict from aggregated result
        
        Returns:
            Tuple of (is_ai_generated, verdict_description)
        """
        prob = aggregated.final_probability
        conf = aggregated.confidence_score
        
        if prob >= 0.8 and conf >= 0.7:
            return True, "High confidence AI-generated"
        elif prob >= 0.6 and conf >= 0.5:
            return True, "Likely AI-generated"
        elif prob >= 0.4 and conf >= 0.5:
            return False, "Uncertain - possible AI elements"
        elif prob < 0.3 and conf >= 0.7:
            return False, "High confidence authentic"
        else:
            return False, "Likely authentic"


# Add missing import
from typing import Optional
