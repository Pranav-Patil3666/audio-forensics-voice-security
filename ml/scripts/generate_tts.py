import os
import random
import subprocess
from TTS.api import TTS

# ==============================
# BASE PATH
# ==============================
BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

# ==============================
# PATHS
# ==============================
output_dir = os.path.join(BASE, "data", "processed", "fake", "tts")
text_file = os.path.join(BASE, "scripts", "tts_texts.txt")

os.makedirs(output_dir, exist_ok=True)

# ==============================
# CONFIG
# ==============================
TARGET = 4000
SAMPLE_RATE = 16000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# ==============================
# LOAD TEXTS
# ==============================
print("📄 Loading text corpus...")

with open(text_file, "r", encoding="utf-8") as f:
    texts = [line.strip() for line in f if line.strip()]

if len(texts) == 0:
    raise ValueError("❌ No text found in tts_texts.txt")

print(f"✅ Loaded {len(texts)} text samples")

# ==============================
# LOAD MODEL
# ==============================
print("🔄 Loading TTS model...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

speakers = tts.speakers if hasattr(tts, "speakers") else [None]
languages = ["en", "hi"]

# ==============================
# TEXT VARIATION (IMPORTANT)
# ==============================
def vary_text(text):
    if random.random() < 0.3:
        text = text.lower()
    if random.random() < 0.2:
        text += " please"
    if random.random() < 0.2:
        text = text.replace(" ", "  ")
    if random.random() < 0.1:
        text += " now"
    return text

# ==============================
# GENERATION LOOP
# ==============================
count = 0

print("🚀 Generating TTS dataset...")

while count < TARGET:
    try:
        base_text = random.choice(texts)
        text = vary_text(base_text)

        speaker = random.choice(speakers)  #type: ignore
        lang = random.choice(languages)

        temp_path = os.path.join(output_dir, f"temp_{count}.wav")
        final_path = os.path.join(output_dir, f"tts_{count}.wav")

        # =========================
        # GENERATE AUDIO
        # =========================
        tts.tts_to_file(
            text=text,
            speaker=speaker,   #type: ignore
            language=lang,
            file_path=temp_path
        )

        # =========================
        # NORMALIZE AUDIO
        # =========================
        cmd = [
            "ffmpeg",
            "-loglevel", "error",
            "-y",
            "-i", temp_path,
            "-ar", str(SAMPLE_RATE),
            "-ac", "1",
            final_path
        ]
        subprocess.run(cmd)

        if os.path.exists(final_path):
            os.remove(temp_path)
            count += 1

        if count % 500 == 0:
            print(f"Generated: {count}")

    except Exception as e:
        print(f"⚠️ Skipping error: {e}")
        continue

print(f"✅ Generated {count} TTS samples")