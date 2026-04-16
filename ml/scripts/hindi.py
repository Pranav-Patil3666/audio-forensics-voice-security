import pandas as pd
import shutil
import os

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

hindi_root = os.path.join(
    BASE,
    "datasets",
    "mozilla hindi",
    "cv-corpus-25.0-2026-03-09",
    "hi"
)

tsv_path = os.path.join(hindi_root, "validated.tsv")
clips_path = os.path.join(hindi_root, "clips")

print("Using path:", tsv_path)

df = pd.read_csv(tsv_path, sep="\t")

subset = df.sample(n=1500)

output_dir = os.path.join(BASE, "data", "real", "hindi")
os.makedirs(output_dir, exist_ok=True)

copied = 0

for _, row in subset.iterrows():
    src = os.path.join(clips_path, row["path"])
    dst = os.path.join(output_dir, row["path"])

    if os.path.exists(src):
        shutil.copy(src, dst)
        copied += 1

print(f"Done. Copied {copied} files.")