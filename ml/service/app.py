from fastapi import FastAPI, UploadFile, File
import torch
import librosa
import numpy as np
import io
import os
import sys
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)

from model import CNNModel
from vad import is_speech

app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn_best.pth")
THRESHOLD = 0.50

model = CNNModel().to(device)
model.load_state_dict(
    torch.load(MODEL_PATH, map_location=device, weights_only=True)  # fixed
)
model.eval()
print("✅ ML model loaded")


def audio_to_tensor(file_bytes):
    try:
        sr_target = 16000
        duration = 2
        max_len = sr_target * duration

        y, sr = librosa.load(io.BytesIO(file_bytes), sr=sr_target, mono=True)

        if not is_speech(y, sr):
            return None

        if len(y) < max_len:
            y = np.pad(y, (0, max_len - len(y)))
        else:
            y = y[:max_len]

        mel = librosa.feature.melspectrogram(
            y=y, sr=sr_target, n_mels=128, n_fft=1024, hop_length=512
        )
        mel = librosa.power_to_db(mel, ref=np.max)
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)
        mel = torch.tensor(mel).unsqueeze(0).float()  # (1, 128, T)

        return mel

    except Exception as e:
        raise Exception(f"Audio processing failed: {str(e)}")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        x = audio_to_tensor(contents)

        if x is None:
            return {"skip": True}

        x = x.unsqueeze(0).to(device)  # (1, 1, 128, T)

        with torch.no_grad():
            outputs = model(x)
            probs = torch.softmax(outputs, dim=1)

        real_prob = probs[0][0].item()
        fake_prob = probs[0][1].item()

        label = "FAKE" if fake_prob >= THRESHOLD else "REAL"
        confidence = fake_prob if label == "FAKE" else real_prob
        risk = "HIGH" if fake_prob >= 0.75 else "MEDIUM" if fake_prob >= 0.50 else "LOW"

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "risk": risk,
            "real_prob": round(real_prob, 4),
            "fake_prob": round(fake_prob, 4),
            "threshold": THRESHOLD
        }

    except Exception as e:
        logger.exception("Prediction failed")
        return {"error": str(e)}