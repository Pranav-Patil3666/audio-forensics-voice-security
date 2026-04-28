import os
import subprocess

INPUT_DIR = "../data/yt/raw_yt"
OUTPUT_DIR = "../data/yt/processed_yt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".wav"):
        inp = os.path.join(INPUT_DIR, file)
        out = os.path.join(OUTPUT_DIR, file)

        cmd = f'ffmpeg -y -i "{inp}" -ar 16000 -ac 1 "{out}"'
        subprocess.run(cmd, shell=True)

print("✅ Normalization done")