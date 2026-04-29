import os
import subprocess
from pathlib import Path

INPUT_DIR = Path("../data/yt/processed_yt")
OUTPUT_DIR = Path("../data/yt/chunks_yt")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_DURATION = 4
STEP = 2  # 🔥 50% overlap
MIN_FILE_SIZE_KB = 20


def run_ffmpeg_chunk(input_path: Path, start: float, output_path: Path):
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-ss", str(start),
        "-i", str(input_path),
        "-t", str(CHUNK_DURATION),
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    return result.returncode == 0


def cleanup_small_files(files):
    removed = 0
    for file in files:
        if file.exists() and file.stat().st_size < MIN_FILE_SIZE_KB * 1024:
            file.unlink()
            removed += 1
    return removed


def get_duration(file: Path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def process_all():
    for file in INPUT_DIR.glob("*.wav"):
        print(f"🎧 Processing: {file.name}")

        duration = get_duration(file)

        base = file.stem
        generated_files = []

        start = 0
        index = 0

        while start < duration:
            output_path = OUTPUT_DIR / f"{base}_{index:05d}.wav"

            ok = run_ffmpeg_chunk(file, start, output_path)

            if ok:
                generated_files.append(output_path)

            start += STEP  # 🔥 overlap
            index += 1

        removed = cleanup_small_files(generated_files)

        print(f"   ✅ Done | Chunks: {len(generated_files)} | Removed: {removed}")

    print("🚀 Splitting pipeline complete")


if __name__ == "__main__":
    process_all()