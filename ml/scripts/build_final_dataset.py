import os
import random
import shutil
from pathlib import Path
from collections import defaultdict

BASE = Path(r"D:\ml-project\Audio Forensics for Voice Security\ml")

REAL_DIR = BASE / "data" / "processed" / "real"
FAKE_DIR = BASE / "data" / "processed" / "fake"
OUTPUT_DIR = BASE / "data" / "final"

TARGET_PER_CLASS = 20000

TRAIN_SPLIT = 0.8
VAL_SPLIT = 0.1

random.seed(42)

# ==============================
# GROUP BY SOURCE (CRITICAL FIX)
# ==============================
def group_files(root):
    groups = []

    for sub in root.iterdir():
        if sub.is_dir():
            sub_name = sub.name.lower()

            for f in sub.glob("*.*"):

                # 🎯 ONLY group YouTube data (real leakage risk)
                if sub_name == "youtube":
                    key = f.name.rsplit("_", 1)[0]
                else:
                    # treat each file as its own group
                    key = f.name

                groups.append((key, f))

    # convert to grouped dict
    from collections import defaultdict
    grouped = defaultdict(list)

    for key, f in groups:
        grouped[key].append(f)

    return list(grouped.values())
print("📦 Grouping data...")

real_groups = group_files(REAL_DIR)
fake_groups = group_files(FAKE_DIR)

random.shuffle(real_groups)
random.shuffle(fake_groups)

# ==============================
# LIMIT SIZE
# ==============================
def limit_groups(groups, target):
    selected = []
    total = 0

    for g in groups:
        if total >= target:
            break
        selected.append(g)
        total += len(g)

    return selected

real_groups = limit_groups(real_groups, TARGET_PER_CLASS)
fake_groups = limit_groups(fake_groups, TARGET_PER_CLASS)

print(f"Real groups: {len(real_groups)}")
print(f"Fake groups: {len(fake_groups)}")

# ==============================
# SPLIT GROUPS (NO LEAKAGE)
# ==============================
def split_groups(groups):
    n = len(groups)
    train = groups[:int(n * TRAIN_SPLIT)]
    val = groups[int(n * TRAIN_SPLIT):int(n * (TRAIN_SPLIT + VAL_SPLIT))]
    test = groups[int(n * (TRAIN_SPLIT + VAL_SPLIT)):]
    return train, val, test

real_train, real_val, real_test = split_groups(real_groups)
fake_train, fake_val, fake_test = split_groups(fake_groups)

# ==============================
# COPY
# ==============================
def copy_groups(groups, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    i = 0
    for g in groups:
        for f in g:
            dst = out_dir / f"{i}{f.suffix}"
            shutil.copy(f, dst)
            i += 1

# ==============================
# BUILD DATASET
# ==============================
print("🚀 Building dataset...")

for split, r, f in [
    ("train", real_train, fake_train),
    ("val", real_val, fake_val),
    ("test", real_test, fake_test),
]:
    print(f"➡️ {split}")

    copy_groups(r, OUTPUT_DIR / split / "real")
    copy_groups(f, OUTPUT_DIR / split / "fake")

print("✅ Leakage-safe dataset ready")