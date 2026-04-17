import os
import librosa
import numpy as np
import soundfile as sf
import random

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

real_dir = os.path.join(BASE, "data", "real", "hindi")
fake_dir = os.path.join(BASE, "data", "fake", "basic")

os.makedirs(fake_dir, exist_ok=True)

files = os.listdir(real_dir)

for i, file in enumerate(files[:1000]):
    path = os.path.join(real_dir, file)

    try:
        y, sr = librosa.load(path, sr=None, mono=True)

        # 🔥 SAFE transformations ONLY
        choice = random.choice(["noise", "volume", "crop"])

        if choice == "noise":
            noise = np.random.randn(len(y)) * 0.003
            y_mod = y + noise

        elif choice == "volume":
            factor = random.uniform(0.5, 1.5)
            y_mod = y * factor

        else:  # crop / truncate (simulates call cuts)
            start = random.randint(0, len(y)//4)
            end = start + int(len(y) * 0.7)
            y_mod = y[start:end]

        # normalize
        y_mod = y_mod / (np.max(np.abs(y_mod)) + 1e-6)

        out_path = os.path.join(fake_dir, f"fake_{i}.wav")
        sf.write(out_path, y_mod, sr)

    except Exception as e:
        print(f"Skipping {file}: {e}")

print("✅ Basic synthetic dataset created (stable)")