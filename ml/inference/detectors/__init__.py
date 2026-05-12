from .base_detector import BaseDetector
from .cnn_detector import CNNDetector
from .wav2vec2_detector import Wav2Vec2Detector

__all__ = [
    "BaseDetector",
    "CNNDetector",
    "Wav2Vec2Detector",
]