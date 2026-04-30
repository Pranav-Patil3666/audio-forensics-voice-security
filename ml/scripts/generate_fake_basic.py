import os
import librosa
import numpy as np
import soundfile as sf
import random
import subprocess
from pathlib import Path

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

# ✅ INPUT (processed real data)
real_dir = os.path.join(BASE, "data", "processed", "real", "common_voice")

# ✅ OUTPUT (fixed)
fake_dir = os.path.join(BASE, "data", "processed", "fake", "augmented")
os.makedirs(fake_dir, exist_ok=True)

files = os.listdir(real_dir)

TARGET_FAKE = 5000  # 🔥 increase scale
generated = 0

print("🚀 Generating augmented fake data...")

while generated < TARGET_FAKE:
    file = random.choice(files)
    path = os.path.join(real_dir, file)

    try:
        y, sr = librosa.load(path, sr=16000, mono=True)

        # 🔥 choose transformation type
        choice = random.choice([
            "noise",
            "pitch",
            "speed",
            "volume",
            "crop",
            "compression"
        ])

        # =========================
        # AUGMENTATIONS
        # =========================
        if choice == "noise":
            noise = np.random.randn(len(y)) * random.uniform(0.002, 0.01)
            y_mod = y + noise

        elif choice == "pitch":
            steps = random.uniform(-3, 3)
            y_mod = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)

        elif choice == "speed":
            rate = random.uniform(0.8, 1.25)
            y_mod = librosa.effects.time_stretch(y, rate) # type: ignore

        elif choice == "volume":
            factor = random.uniform(0.4, 1.6)
            y_mod = y * factor

        elif choice == "crop":
            if len(y) > sr * 2:
                start = random.randint(0, len(y) - sr)  # type: ignore
                y_mod = y[start:start + int(sr * random.uniform(1.5, 3))]
            else:
                y_mod = y

        elif choice == "compression":
            # temporary file
            temp_in = "temp_in.wav"
            temp_out = "temp_out.wav"

            sf.write(temp_in, y, sr)

            bitrate = random.choice(["16k", "32k", "64k"])
            cmd = f'ffmpeg -loglevel error -y -i "{temp_in}" -b:a {bitrate} "{temp_out}"'
            subprocess.run(cmd, shell=True)

            if os.path.exists(temp_out):
                y_mod, sr = librosa.load(temp_out, sr=16000, mono=True)
                os.remove(temp_in)
                os.remove(temp_out)
            else:
                y_mod = y

        # =========================
        # NORMALIZATION
        # =========================
        y_mod = y_mod / (np.max(np.abs(y_mod)) + 1e-6)

        # =========================
        # SAVE
        # =========================
        out_path = os.path.join(fake_dir, f"fake_{generated}.wav")
        sf.write(out_path, y_mod, 16000)

        generated += 1

        if generated % 500 == 0:
            print(f"Generated: {generated}")

    except Exception as e:
        continue

print(f"✅ Generated {generated} augmented fake samples")