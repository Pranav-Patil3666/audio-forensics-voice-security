from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import librosa
import numpy as np
import torch

from ..config import PATHS, THRESHOLDS, RUNTIME
from ..schemas import AudioLabel
from ..utils.audio import load_audio, pad_or_trim, audio_duration
from .base_detector import BaseDetector , RawPrediction

# Make ml/src importable for CNNModel
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from model import CNNModel  # noqa: E402


class CNNDetector(BaseDetector):
    """
    CNN detector aligned with:
      - ml/src/dataset.py
      - mel spectrogram training pipeline
      - 16kHz mono
      - 2 sec fixed-length input
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        threshold: float | None = None,
        device=None,
        logger=None,
    ) -> None:
        self.model_path = Path(model_path or PATHS.cnn_best_path)
        self.sample_rate = RUNTIME.sample_rate
        self.duration_sec = RUNTIME.cnn_chunk_duration_sec
        self.max_length = int(self.sample_rate * self.duration_sec)

        super().__init__(
            detector_name="cnn",
            model_version=PATHS.snapshot_name,
            threshold=threshold if threshold is not None else THRESHOLDS.cnn_fake_threshold,
            device=device,
            logger=logger,
        )

    def load(self) -> None:
        self.logger.info(f"Loading CNN model from: {self.model_path}")

        self.model = CNNModel().to(self.device)
        state_dict = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

        self.logger.info("CNN model loaded successfully")

    def _audio_to_tensor(self, file_path: Path) -> tuple[torch.Tensor, Dict[str, Any]]:
        y, sr = load_audio(file_path, sample_rate=self.sample_rate, mono=True, normalize=False)

        duration = audio_duration(y, sr)

        if len(y) < self.max_length:
            y = pad_or_trim(y, self.max_length, random_crop=False)
        else:
            y = y[:self.max_length]

        mel = librosa.feature.melspectrogram(
            y=y,
            sr=self.sample_rate,
            n_mels=128,
            n_fft=1024,
            hop_length=512,
            fmin=20,
            fmax=8000,
        )

        mel_db = librosa.power_to_db(mel, ref=np.max)
        mel_db = (mel_db - mel_db.mean()) / (mel_db.std() + 1e-6)

        x = torch.tensor(mel_db, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        meta = {
            "sample_rate": self.sample_rate,
            "duration_sec": float(duration),
            "input_shape": list(x.shape),
            "max_length": self.max_length,
            "pipeline": "cnn_mel_v1",
        }
        return x, meta

    def _predict_raw(self, file_path: Path) -> RawPrediction:
        x, meta = self._audio_to_tensor(file_path)
        x = x.to(self.device)

        with torch.inference_mode():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=-1)[0]

        real_prob = float(probs[0].item())
        fake_prob = float(probs[1].item())

        meta.update(
            {
                "model_path": str(self.model_path),
                "threshold": self.threshold,
            }
        )

        return RawPrediction(
            real_prob=real_prob,
            fake_prob=fake_prob,
            skip=False,
            meta=meta,
        )