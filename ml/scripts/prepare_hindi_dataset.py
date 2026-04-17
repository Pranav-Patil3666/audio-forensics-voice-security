import os
import shutil
import pandas as pd

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

# 🔴 YOUR ACTUAL PATH (update if needed)
hindi_root = os.path.join(
    BASE,
    "datasets",
    "mozilla hindi",
    "cv-corpus-25.0-2026-03-09",
    "hi"
)

tsv_path = os.path.join(hindi_root, "validated.tsv")
clips_path = os.path.join(hindi_root, "clips")

output_dir = os.path.join(BASE, "data", "real", "hindi")
os.makedirs(output_dir, exist_ok=True)

print("Reading dataset...")
df = pd.read_csv(tsv_path, sep="\t")

# 🔥 take subset (not full 19k)
subset = df.sample(n=1500)

count = 0

for _, row in subset.iterrows():
    src = os.path.join(clips_path, row["path"])
    dst = os.path.join(output_dir, f"{count}.wav")

    if os.path.exists(src):
        try:
            shutil.copy(src, dst)
            count += 1
        except:
            continue

print(f"Copied {count} Hindi samples")