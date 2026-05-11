from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict

from ._base import ML_ROOT, env_str, ensure_path


@dataclass(slots=True)
class ModelPaths:
    snapshot_name: str = field(default_factory=lambda: env_str("SATARKRAHE_ACTIVE_SNAPSHOT", "run_001"))

    ml_root: Path = field(default=ML_ROOT, init=False)
    outputs_root: Path = field(init=False)
    snapshots_root: Path = field(init=False)
    snapshot_root: Path = field(init=False)

    cnn_root: Path = field(init=False)
    cnn_best_dir: Path = field(init=False)
    cnn_best_path: Path = field(init=False)
    cnn_report_path: Path = field(init=False)

    wav2vec2_root: Path = field(init=False)
    wav2vec2_best_dir: Path = field(init=False)
    wav2vec2_report_path: Path = field(init=False)

    runtime_root: Path = field(init=False)
    logs_root: Path = field(init=False)

    def __post_init__(self) -> None:
        self.outputs_root = ensure_path(self.ml_root / "outputs")
        self.snapshots_root = ensure_path(self.outputs_root / "snapshots")
        self.snapshot_root = ensure_path(self.snapshots_root / self.snapshot_name)

        self.cnn_root = ensure_path(self.snapshot_root / "cnn")
        self.cnn_best_dir = ensure_path(self.cnn_root / "best")
        self.cnn_best_path = ensure_path(self.cnn_best_dir / "cnn_best.pth")
        self.cnn_report_path = ensure_path(self.cnn_root / "cnn_test_report.json")

        self.wav2vec2_root = ensure_path(self.snapshot_root / "wav2vec2_base")
        self.wav2vec2_best_dir = ensure_path(self.wav2vec2_root / "best")
        self.wav2vec2_report_path = ensure_path(self.wav2vec2_root / "evaluation" / "wav2vec2_test_report.json")

        self.runtime_root = ensure_path(self.outputs_root / "runtime")
        self.logs_root = ensure_path(self.outputs_root / "logs")

    def to_dict(self) -> Dict[str, str]:
        return {
            "ml_root": str(self.ml_root),
            "outputs_root": str(self.outputs_root),
            "snapshots_root": str(self.snapshots_root),
            "snapshot_root": str(self.snapshot_root),
            "cnn_best_dir": str(self.cnn_best_dir),
            "cnn_best_path": str(self.cnn_best_path),
            "cnn_report_path": str(self.cnn_report_path),
            "wav2vec2_best_dir": str(self.wav2vec2_best_dir),
            "wav2vec2_report_path": str(self.wav2vec2_report_path),
            "runtime_root": str(self.runtime_root),
            "logs_root": str(self.logs_root),
        }


PATHS = ModelPaths()