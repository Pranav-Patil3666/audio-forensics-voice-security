import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

# INPUT DIRECTORIES
real_dir = os.path.join(BASE, "data", "real", "hindi")
fake_dirs = [
    os.path.join(BASE, "data", "fake", "basic"),
    os.path.join(BASE, "data", "fake", "tts"),
    os.path.join(BASE, "data", "fake_aug", "compressed"),
]

# OUTPUT
spec_base = os.path.join(BASE, "features", "spectrograms")
real_out = os.path.join(spec_base, "real")
fake_out = os.path.join(spec_base, "fake")

os.makedirs(real_out, exist_ok=True)
os.makedirs(fake_out, exist_ok=True)

labels = []

# 🔥 Function to create spectrogram
def save_spectrogram(audio_path, output_path):
    y, sr = librosa.load(audio_path, sr=16000)

    # Mel spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    S_db = librosa.power_to_db(S, ref=np.max)

    plt.figure(figsize=(3, 3))
    plt.axis('off')
    plt.imshow(S_db, aspect='auto', origin='lower')

    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()


# 🟢 Process REAL
print("Processing REAL...")
for i, file in enumerate(os.listdir(real_dir)[:1500]):
    path = os.path.join(real_dir, file)

    try:
        out_path = os.path.join(real_out, f"real_{i}.png")
        save_spectrogram(path, out_path)

        labels.append([out_path, 0])  # 0 = real

    except Exception as e:
        print("Error:", e)


# 🔴 Process FAKE
print("Processing FAKE...")
count = 0

for fake_dir in fake_dirs:
    if not os.path.exists(fake_dir):
        continue

    for file in os.listdir(fake_dir):
        path = os.path.join(fake_dir, file)

        try:
            out_path = os.path.join(fake_out, f"fake_{count}.png")
            save_spectrogram(path, out_path)

            labels.append([out_path, 1])  # 1 = fake
            count += 1

        except Exception as e:
            print("Error:", e)


# 💾 Save labels
df = pd.DataFrame(labels, columns=["path", "label"])
df.to_csv(os.path.join(spec_base, "labels.csv"), index=False)

print("✅ Spectrogram generation complete")