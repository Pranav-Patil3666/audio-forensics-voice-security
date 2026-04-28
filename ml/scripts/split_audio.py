import os
import subprocess

INPUT_DIR = "../data/yt/processed_yt"
OUTPUT_DIR = "../data/yt/chunks_yt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNK_DURATION = 4  # seconds

for file in os.listdir(INPUT_DIR):
    if file.endswith(".wav"):
        inp = os.path.join(INPUT_DIR, file)
        base = os.path.splitext(file)[0]

        out_pattern = os.path.join(OUTPUT_DIR, f"{base}_%05d.wav")

        cmd = (
            f'ffmpeg -y -i "{inp}" '
            f'-f segment -segment_time {CHUNK_DURATION} '
            f'-ar 16000 -ac 1 "{out_pattern}"'
        )

        subprocess.run(cmd, shell=True)

print("✅ Splitting done")