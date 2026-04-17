from pydub import AudioSegment
import os

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

input_dir = os.path.join(BASE, "data", "fake", "basic")
output_dir = os.path.join(BASE, "data", "fake_aug", "compressed")

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir)[:500]:
    path = os.path.join(input_dir, file)

    try:
        audio = AudioSegment.from_file(path)

        audio = audio.set_frame_rate(8000).set_channels(1)

        out_path = os.path.join(output_dir, f"comp_{file}")
        audio.export(out_path, format="wav")

    except Exception as e:
        print("Error:", e)

print("Compressed dataset created")