import torch
import librosa
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms
import os

from model import CNNModel

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"
MODEL_PATH = os.path.join(BASE, "models", "cnn_model_best.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# LOAD MODEL (safe)
# =========================
model = CNNModel().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# =========================
# TRANSFORM
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# =========================
# AUDIO → SPECTROGRAM (NO TEMP FILE)
# =========================
def audio_to_spectrogram(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"File not found: {audio_path}")

    y, sr = librosa.load(audio_path, sr=16000)

    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=128,
        fmin=20,
        fmax=8000
    )
    S_db = librosa.power_to_db(S, ref=np.max)

    # Convert directly to image (no disk write)
    fig = plt.figure(figsize=(2.24, 2.24), dpi=100)
    plt.axis("off")
    plt.imshow(S_db, aspect='auto', origin='lower', cmap="viridis")

    fig.canvas.draw()

    # Convert to numpy array
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)  
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)

    # Convert to grayscale PIL
    image = Image.fromarray(image).convert("L")

    image = transform(image).unsqueeze(0)

    return image

# =========================
# PREDICTION (IMPROVED)
# =========================
def predict(audio_path):
    image = audio_to_spectrogram(audio_path).to(device)

    with torch.no_grad():
        outputs = model(image)
        probs = torch.softmax(outputs, dim=1)

    real_prob = probs[0][0].item()
    fake_prob = probs[0][1].item()

    # Label decision
    if fake_prob > real_prob:
        label = "FAKE"
        confidence = fake_prob
    else:
        label = "REAL"
        confidence = real_prob

    # 🔥 Risk interpretation
    if confidence > 0.9:
        risk = "LOW RISK"
    elif confidence > 0.75:
        risk = "MEDIUM RISK"
    else:
        risk = "HIGH RISK ⚠️"

    return label, confidence, risk, real_prob, fake_prob


# =========================
# TEST
# =========================
if __name__ == "__main__":
    test_audio = input("Enter audio path: ").strip()

    try:
        label, confidence, risk, real_p, fake_p = predict(test_audio)

        print("\n==============================")
        print(f"Prediction : {label}")
        print(f"Confidence : {confidence:.4f}")
        print(f"Risk Level : {risk}")
        print(f"(Real: {real_p:.4f} | Fake: {fake_p:.4f})")
        print("==============================\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")