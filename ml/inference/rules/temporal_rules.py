from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

from ..config import THRESHOLDS
from ..schemas import AudioLabel, RiskLevel, SessionState


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_label(value: Any) -> AudioLabel:
    if isinstance(value, AudioLabel):
        return value
    try:
        return AudioLabel(str(value))
    except Exception:
        return AudioLabel.UNKNOWN


def _risk_hint(score: float) -> RiskLevel:
    if score >= THRESHOLDS.high_risk_threshold:
        return RiskLevel.HIGH
    if score >= THRESHOLDS.medium_risk_threshold:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


@dataclass(slots=True)
class TemporalRuleResult:
    score: float
    skip: bool
    risk_hint: RiskLevel
    votes: Dict[str, float] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp_utc: str = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": float(self.score),
            "skip": bool(self.skip),
            "risk_hint": self.risk_hint.value,
            "votes": self.votes,
            "reasons": self.reasons,
            "details": self.details,
            "timestamp_utc": self.timestamp_utc,
        }


def evaluate_temporal_consistency(
    session_state: SessionState | None,
    *,
    current_fake_prob: float | None = None,
    current_label: AudioLabel | str | None = None,
    window: int | None = None,
) -> TemporalRuleResult:
    """
    Looks at chunk history and detects:
      - fake streaks
      - persistent medium suspicion
      - sudden spikes
      - oscillation / instability
      - rising fake trend
    """

    if session_state is None:
        return TemporalRuleResult(
            score=0.0,
            skip=False,
            risk_hint=RiskLevel.LOW,
            votes={"no_session_state": 1.0},
            reasons=["no_session_state"],
            details={},
        )

    window = int(window or min(session_state.rolling_window, THRESHOLDS.fake_high_count_window))
    window = max(1, window)

    probs = list(session_state.recent_fake_probs(window))

    if current_fake_prob is not None:
        probs.append(float(current_fake_prob))

    if not probs:
        return TemporalRuleResult(
            score=0.0,
            skip=False,
            risk_hint=RiskLevel.LOW,
            votes={"no_recent_probs": 1.0},
            reasons=["no_recent_probs"],
            details={"window": window},
        )

    labels = [obs.label for obs in session_state.recent_chunks(window)]
    if current_label is not None:
        labels.append(_to_label(current_label))

    probs_arr = np.asarray(probs, dtype=np.float32)

    high_hits = int(np.sum(probs_arr >= THRESHOLDS.high_risk_threshold))
    medium_hits = int(np.sum(probs_arr >= THRESHOLDS.medium_risk_threshold))

    streak_score = _clamp01(high_hits / max(1, THRESHOLDS.fake_high_count_min_hits))
    medium_score = _clamp01(medium_hits / max(1, len(probs_arr)))
    trend_score = _clamp01(max(0.0, float(probs_arr[-1] - probs_arr[0])))
    spike_delta = float(np.max(np.abs(np.diff(probs_arr)))) if len(probs_arr) >= 2 else 0.0
    spike_score = _clamp01((spike_delta - THRESHOLDS.spike_delta) / max(1e-8, 1.0 - THRESHOLDS.spike_delta))

    flips = 0
    cleaned_labels = [lab for lab in labels if lab != AudioLabel.UNKNOWN]
    for i in range(1, len(cleaned_labels)):
        if cleaned_labels[i] != cleaned_labels[i - 1]:
            flips += 1
    oscillation_score = _clamp01(flips / max(1, len(cleaned_labels) - 1))

    fake_streak = session_state.fake_streak
    persistent_fake_score = _clamp01(fake_streak / max(1, THRESHOLDS.fake_high_count_min_hits))

    score = (
        0.30 * streak_score
        + 0.20 * medium_score
        + 0.20 * spike_score
        + 0.15 * trend_score
        + 0.15 * oscillation_score
    )

    if fake_streak >= THRESHOLDS.fake_high_count_min_hits:
        score = max(score, 0.85)

    votes = {
        "streak_score": float(streak_score),
        "medium_score": float(medium_score),
        "spike_score": float(spike_score),
        "trend_score": float(trend_score),
        "oscillation_score": float(oscillation_score),
        "persistent_fake_score": float(persistent_fake_score),
    }

    reasons: List[str] = []
    if high_hits >= THRESHOLDS.fake_high_count_min_hits:
        reasons.append("persistent_high_fake")
    if medium_hits >= THRESHOLDS.medium_count_min_hits:
        reasons.append("persistent_medium_fake")
    if spike_delta >= THRESHOLDS.spike_delta:
        reasons.append("sudden_probability_spike")
    if flips >= 2:
        reasons.append("label_oscillation")
    if trend_score >= 0.25:
        reasons.append("rising_fake_trend")
    if fake_streak >= THRESHOLDS.fake_high_count_min_hits:
        reasons.append("fake_streak")

    details = {
        "window": window,
        "probs": [float(p) for p in probs],
        "labels": [lab.value if isinstance(lab, AudioLabel) else str(lab) for lab in cleaned_labels],
        "high_hits": high_hits,
        "medium_hits": medium_hits,
        "fake_streak": fake_streak,
        "real_streak": session_state.real_streak,
        "spike_delta": float(spike_delta),
        "flips": flips,
        "smoothed_fake_prob": float(session_state.smoothed_fake_prob),
    }

    return TemporalRuleResult(
        score=_clamp01(score),
        skip=False,
        risk_hint=_risk_hint(score),
        votes=votes,
        reasons=reasons,
        details=details,
    )