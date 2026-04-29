import os
import subprocess
from pathlib import Path

INPUT_DIR = Path("../data/yt/raw_yt")
OUTPUT_DIR = Path("../data/yt/processed_yt")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for file in INPUT_DIR.glob("*.wav"):
    out_file = OUTPUT_DIR / file.name

    print(f"🎧 Normalizing: {file.name}")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(file),
        "-ar", "16000",
        "-ac", "1",
        str(out_file)
    ]

    subprocess.run(cmd)

print("✅ Normalization complete")