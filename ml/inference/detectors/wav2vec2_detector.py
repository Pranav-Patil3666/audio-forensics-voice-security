from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, Tuple          # Tuple removed — no longer used anywhere

import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification, BatchFeature

from ..config import PATHS, THRESHOLDS, RUNTIME
from ..utils.audio import load_audio, pad_or_trim, audio_duration
from .base_detector import BaseDetector, RawPrediction


class Wav2Vec2Detector(BaseDetector):
    """
    Wav2Vec2 detector aligned with:
      - ml/wav2vec/wav2vec_dataset.py
      - 16kHz raw waveform input
      - 2 sec fixed-length input
      - binary REAL/FAKE classification
    """

    def __init__(
        self,
        model_dir: str | Path | None = None,
        threshold: float | None = None,
        device=None,
        logger=None,
    ) -> None:
        self.model_dir = Path(model_dir or PATHS.wav2vec2_best_dir)
        self.sample_rate = RUNTIME.sample_rate
        self.duration_sec = RUNTIME.wav2vec2_duration_sec
        self.max_length = int(self.sample_rate * self.duration_sec)

        self.feature_extractor: Wav2Vec2FeatureExtractor | None = None

        super().__init__(
            detector_name="wav2vec2",
            model_version=PATHS.snapshot_name,
            threshold=threshold if threshold is not None else THRESHOLDS.wav2vec2_fake_threshold,
            device=device,
            logger=logger,
        )

    def load(self) -> None:
        self.logger.info(f"Loading Wav2Vec2 model from: {self.model_dir}")

        try:
            self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(str(self.model_dir))
        except Exception as exc:
            warnings.warn(
                f"Feature extractor could not be loaded from {self.model_dir}. "
                f"Falling back to facebook/wav2vec2-base. Reason: {exc}"
            )
            self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base")

        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(str(self.model_dir))
        self.model.to(self.device)
        self.model.eval()

        self.logger.info("Wav2Vec2 model loaded successfully")

    def _audio_to_inputs(self, file_path: Path) -> tuple[BatchFeature, Dict[str, Any]]:
        # lowercase tuple[...] is fine — Python 3.9+ built-in generic, no import needed
        if self.feature_extractor is None:
            raise RuntimeError("Feature extractor is not loaded")

        y, sr = load_audio(file_path, sample_rate=self.sample_rate, mono=True, normalize=False)
        duration = audio_duration(y, sr)

        if len(y) < self.max_length:
            y = pad_or_trim(y, self.max_length, random_crop=False)
        else:
            y = y[:self.max_length]

        inputs = self.feature_extractor(
            y,
            sampling_rate=self.sample_rate,
            return_tensors="pt",
            padding=False,
        )

        meta = {
            "sample_rate": self.sample_rate,
            "duration_sec": float(duration),
            "input_shape": list(inputs["input_values"].shape),
            "max_length": self.max_length,
            "pipeline": "wav2vec2_raw_waveform_v1",
        }

        return inputs, meta

    def _predict_raw(self, file_path: Path) -> RawPrediction:  
        inputs, meta = self._audio_to_inputs(file_path)

        input_values = inputs["input_values"].to(self.device)

        with torch.inference_mode():
            outputs = self.model(input_values=input_values)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]

        real_prob = float(probs[0].item())
        fake_prob = float(probs[1].item())

        meta.update(
            {
                "model_dir": str(self.model_dir),
                "threshold": self.threshold,
            }
        )

        return RawPrediction(
            real_prob=real_prob,
            fake_prob=fake_prob,
            skip=False,
            meta=meta,
        )