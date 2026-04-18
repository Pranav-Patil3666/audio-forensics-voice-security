import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

# ==============================
# INPUT (ASVspoof)
# ==============================
real_dir = os.path.join(BASE, "data", "real", "asvspoof")
fake_dir = os.path.join(BASE, "data", "fake", "asvspoof")

# ==============================
# OUTPUT (existing spectrograms)
# ==============================
spec_base = os.path.join(BASE, "features", "spectrograms")
real_out = os.path.join(spec_base, "real")
fake_out = os.path.join(spec_base, "fake")

os.makedirs(real_out, exist_ok=True)
os.makedirs(fake_out, exist_ok=True)

labels_path = os.path.join(spec_base, "labels.csv")

# ==============================
# LOAD EXISTING LABELS
# ==============================
if os.path.exists(labels_path):
    df_existing = pd.read_csv(labels_path)
    labels = df_existing.values.tolist()

    real_count = sum(1 for x in labels if x[1] == 0)
    fake_count = sum(1 for x in labels if x[1] == 1)

else:
    labels = []
    real_count = 0
    fake_count = 0

print(f"Starting from → real:{real_count}, fake:{fake_count}")

# ==============================
# SPECTROGRAM FUNCTION
# ==============================
def save_spectrogram(audio_path, output_path):
    y, sr = librosa.load(audio_path, sr=16000)

    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=128,
        fmax=8000
    )
    S_db = librosa.power_to_db(S, ref=np.max)

    plt.figure(figsize=(3, 3))
    plt.axis("off")
    plt.imshow(S_db, aspect="auto", origin="lower")

    plt.savefig(output_path, bbox_inches="tight", pad_inches=0)
    plt.close()

# ==============================
# PROCESS REAL (ASVspoof)
# ==============================
print("Processing ASVspoof REAL...")

for file in os.listdir(real_dir):
    path = os.path.join(real_dir, file)

    try:
        out_path = os.path.join(real_out, f"real_{real_count}.png")

        save_spectrogram(path, out_path)

        labels.append([out_path, 0])
        real_count += 1

    except Exception as e:
        print("Error:", e)

# ==============================
# PROCESS FAKE (ASVspoof)
# ==============================
print("Processing ASVspoof FAKE...")

for file in os.listdir(fake_dir):
    path = os.path.join(fake_dir, file)

    try:
        out_path = os.path.join(fake_out, f"fake_{fake_count}.png")

        save_spectrogram(path, out_path)

        labels.append([out_path, 1])
        fake_count += 1

    except Exception as e:
        print("Error:", e)

# ==============================
# SAVE UPDATED LABELS
# ==============================
df = pd.DataFrame(labels, columns=["path", "label"])
df.to_csv(labels_path, index=False)

print("✅ ASVspoof spectrograms added successfully")
print(f"Final count → real:{real_count}, fake:{fake_count}")