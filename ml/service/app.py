from fastapi import FastAPI, UploadFile, File
import torch
import librosa
import numpy as np
from PIL import Image
import io
import os

import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

sys.path.append(SRC_DIR)

from model import CNNModel
from vad import is_speech

app = FastAPI()

# =========================
# DEVICE
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# LOAD MODEL (BEST)
# =========================
MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn_model_best.pth")

model = CNNModel().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

print("✅ ML model loaded")

# =========================
# AUDIO → TENSOR
# =========================
def audio_to_tensor(file_bytes):
    try:
        y, sr = librosa.load(io.BytesIO(file_bytes), sr=16000)
        
        #🔥 VAD check   
        if not is_speech(y, sr):
            return None

        # 🔥 Mel Spectrogram (same as training)
        S = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=128,
            fmin=20,
            fmax=8000
        )

        S_db = librosa.power_to_db(S, ref=np.max)

        # 🔥 Normalize to 0–255 (fix PIL issue)
        S_norm = (S_db - S_db.min()) / (S_db.max() - S_db.min())
        S_img = (S_norm * 255).astype(np.uint8)

        image = Image.fromarray(S_img).convert("L")
        image = image.resize((224, 224))

        # 🔥 SAME normalization as training
        image = np.array(image) / 255.0
        image = (image - 0.5) / 0.5

        image = torch.tensor(image).unsqueeze(0).unsqueeze(0).float()

        return image

    except Exception as e:
        raise Exception(f"Audio processing failed: {str(e)}")

# =========================
# PREDICTION
# =========================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        image = audio_to_tensor(contents)

        # 🔥 skip non-speech
        if image is None:
            return {
                "skip": True
            }

        image = image.to(device)

        with torch.no_grad():
            outputs = model(image)
            probs = torch.softmax(outputs, dim=1)

        real_prob = probs[0][0].item()
        fake_prob = probs[0][1].item()

        # 🔥 Decision logic
        if fake_prob > real_prob:
            label = "FAKE"
            confidence = fake_prob
        else:
            label = "REAL"
            confidence = real_prob

        # 🔥 Risk level
        if confidence > 0.9:
            risk = "LOW"
        elif confidence > 0.75:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "risk": risk,
            "real_prob": round(real_prob, 4),
            "fake_prob": round(fake_prob, 4)
        }

    except Exception as e:
        return {
            "error": str(e)
        }