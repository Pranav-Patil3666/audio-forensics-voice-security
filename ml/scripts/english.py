from datasets import load_dataset, Audio
import soundfile as sf
import os

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

# Load dataset
dataset = load_dataset(
    "mozilla-foundation/common_voice_17_0",
    "en",
    split="train[:2%]"   # reduce for safety
)

# 🔥 IMPORTANT: force audio decoding
dataset = dataset.cast_column("audio", Audio())

output_dir = os.path.join(BASE, "data", "real", "english")
os.makedirs(output_dir, exist_ok=True)

count = 0

for i, sample in enumerate(dataset):
    try:
        audio = sample["audio"]["array"]    # type: ignore
        sr = sample["audio"]["sampling_rate"]   # type: ignore

        sf.write(os.path.join(output_dir, f"{i}.wav"), audio, sr)
        count += 1

    except Exception as e:
        print(f"Skipping {i}: {e}")

print(f"Done. Saved {count} files.")