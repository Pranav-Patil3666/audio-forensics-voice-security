from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..config import ENSEMBLE
from ..schemas import EnsembleWeights


def _get_metric(report: Mapping[str, Any], *paths: str, default: float = 0.0) -> float:
    """
    Safe nested metric lookup.
    Tries multiple dotted paths in order.
    Examples:
      _get_metric(report, "metrics_at_0.50.roc_auc", "roc_auc")
    """
    for path in paths:
        current: Any = report
        ok = True
        for key in path.split("."):
            if isinstance(current, Mapping) and key in current:
                current = current[key]
            else:
                ok = False
                break
        if ok:
            try:
                if isinstance(current, (int, float, str)):  
                    return float(current)
            except (TypeError, ValueError):
                continue
    return float(default)


def report_score(
    report: Mapping[str, Any],
    *,
    roc_weight: float = 0.50,
    real_f1_weight: float = 0.30,
    real_recall_weight: float = 0.20,
) -> float:
    """
    Conservative security-oriented score:
      - ROC AUC captures ranking quality
      - REAL F1 penalizes false alarms
      - REAL recall protects legitimate speakers
    """
    roc_auc = _get_metric(report, "roc_auc", "metrics_at_0.50.roc_auc", "metrics_at_best_threshold.roc_auc", default=0.0)

    # support several report layouts
    real_f1 = _get_metric(
        report,
        "real_f1",
        "metrics_at_0.50.classification_report.REAL.f1-score",
        "metrics_at_best_threshold.classification_report.REAL.f1-score",
        default=0.0,
    )
    real_recall = _get_metric(
        report,
        "real_recall",
        "metrics_at_0.50.classification_report.REAL.recall",
        "metrics_at_best_threshold.classification_report.REAL.recall",
        default=0.0,
    )

    return (
        roc_weight * roc_auc
        + real_f1_weight * real_f1
        + real_recall_weight * real_recall
    )


def derive_weights_from_reports(
    cnn_report: Mapping[str, Any],
    wav2vec2_report: Mapping[str, Any],
    *,
    rules_weight: float = 0.0,
) -> EnsembleWeights:
    """
    Derive static baseline weights from model reports, then normalize.
    With your current reports this lands extremely close to:
      CNN ≈ 0.5125
      Wav2Vec2 ≈ 0.4875
      Rules = 0.0
    """
    cnn_score = report_score(cnn_report)
    wav2vec_score = report_score(wav2vec2_report)

    # Avoid divide-by-zero if reports are malformed
    total = max(cnn_score + wav2vec_score + rules_weight, 1e-8)

    return EnsembleWeights(
        cnn=cnn_score / total,
        wav2vec2=wav2vec_score / total,
        rules=max(0.0, rules_weight) / total,
    )


# Frozen baseline weights for current project state.
# These are the values you should start with until you add the rules layer.
BASELINE_WEIGHTS = EnsembleWeights(
    cnn=0.5125,
    wav2vec2=0.4875,
    rules=0.0,
)