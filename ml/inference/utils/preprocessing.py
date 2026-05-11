from __future__ import annotations

import numpy as np
import torch
import librosa
from PIL import Image


def generate_mel_spectrogram(
    y: np.ndarray,
    sr: int = 16000,
    n_mels: int = 128,
    n_fft: int = 2048,
    hop_length: int = 512,
    fmin: int = 20,
    fmax: int = 8000,
) -> np.ndarray:

    mel = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=n_mels,
        n_fft=n_fft,
        hop_length=hop_length,
        fmin=fmin,
        fmax=fmax,
    )

    mel_db = librosa.power_to_db(mel, ref=np.max)

    return mel_db.astype(np.float32)


def normalize_spectrogram(spec: np.ndarray) -> np.ndarray:

    spec_min = spec.min()
    spec_max = spec.max()

    if spec_max - spec_min < 1e-8:
        return np.zeros_like(spec, dtype=np.float32)

    spec = (spec - spec_min) / (spec_max - spec_min)

    return spec.astype(np.float32)


def spectrogram_to_image(
    spec: np.ndarray,
    image_size: tuple[int, int] = (224, 224),
) -> np.ndarray:

    spec = normalize_spectrogram(spec)

    spec_img = (spec * 255).astype(np.uint8)

    image = Image.fromarray(spec_img).convert("L")
    image = image.resize(image_size)

    image = np.array(image).astype(np.float32) / 255.0

    return image


def image_to_tensor(
    image: np.ndarray,
    normalize: bool = True,
) -> torch.Tensor:

    if normalize:
        image = (image - 0.5) / 0.5

    tensor = torch.tensor(image).unsqueeze(0).unsqueeze(0).float()

    return tensor


def cnn_preprocess_pipeline(
    y: np.ndarray,
    sr: int = 16000,
    image_size: tuple[int, int] = (224, 224),
) -> torch.Tensor:

    mel = generate_mel_spectrogram(
        y=y,
        sr=sr,
    )

    image = spectrogram_to_image(
        mel,
        image_size=image_size,
    )

    tensor = image_to_tensor(image)

    return tensor


def waveform_to_tensor(
    y: np.ndarray,
) -> torch.Tensor:

    return torch.tensor(y).float()


def safe_softmax(
    logits: torch.Tensor,
    dim: int = 1,
) -> torch.Tensor:

    logits = logits - logits.max(dim=dim, keepdim=True).values

    return torch.softmax(logits, dim=dim)


def probabilities_from_logits(
    logits: torch.Tensor,
) -> tuple[float, float]:

    probs = safe_softmax(logits, dim=1)

    real_prob = float(probs[0][0].item())
    fake_prob = float(probs[0][1].item())

    return real_prob, fake_prob