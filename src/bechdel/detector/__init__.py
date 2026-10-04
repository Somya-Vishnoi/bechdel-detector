"""Rule-based Bechdel dialogue detector and evaluation."""

from bechdel.detector.rules import DialogueDetector, ConversationAnalysis
from bechdel.detector.evaluator import evaluate_detector_stages

__all__ = [
    "DialogueDetector",
    "ConversationAnalysis",
    "evaluate_detector_stages",
]
