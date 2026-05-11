from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

from ._base import env_float, env_int


@dataclass(slots=True)
class Thresholds:
    # model decision thresholds
    cnn_fake_threshold: float = env_float("SATARKRAHE_CNN_FAKE_THRESHOLD", 0.50)
    wav2vec2_fake_threshold: float = env_float("SATARKRAHE_WAV2VEC2_FAKE_THRESHOLD", 0.63)

    # session / risk thresholds
    medium_risk_threshold: float = env_float("SATARKRAHE_MEDIUM_RISK_THRESHOLD", 0.55)
    high_risk_threshold: float = env_float("SATARKRAHE_HIGH_RISK_THRESHOLD", 0.75)

    # rule thresholds
    fake_high_count_window: int = env_int("SATARKRAHE_FAKE_HIGH_COUNT_WINDOW", 5)
    fake_high_count_min_hits: int = env_int("SATARKRAHE_FAKE_HIGH_COUNT_MIN_HITS", 3)

    medium_count_min_hits: int = env_int("SATARKRAHE_MEDIUM_COUNT_MIN_HITS", 2)
    spike_delta: float = env_float("SATARKRAHE_SPIKE_DELTA", 0.45)
    disagreement_delta: float = env_float("SATARKRAHE_DISAGREEMENT_DELTA", 0.25)

    # VAD / speech gating
    vad_speech_ratio_threshold: float = env_float("SATARKRAHE_VAD_SPEECH_RATIO_THRESHOLD", 0.30)

    def to_dict(self) -> Dict[str, float | int]:
        return {
            "cnn_fake_threshold": self.cnn_fake_threshold,
            "wav2vec2_fake_threshold": self.wav2vec2_fake_threshold,
            "medium_risk_threshold": self.medium_risk_threshold,
            "high_risk_threshold": self.high_risk_threshold,
            "fake_high_count_window": self.fake_high_count_window,
            "fake_high_count_min_hits": self.fake_high_count_min_hits,
            "medium_count_min_hits": self.medium_count_min_hits,
            "spike_delta": self.spike_delta,
            "disagreement_delta": self.disagreement_delta,
            "vad_speech_ratio_threshold": self.vad_speech_ratio_threshold,
        }


THRESHOLDS = Thresholds()