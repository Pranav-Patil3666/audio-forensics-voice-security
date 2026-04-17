from TTS.api import TTS
import os

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

output_dir = os.path.join(BASE, "data", "fake", "tts")
os.makedirs(output_dir, exist_ok=True)

texts = [
    "Your bank account is under verification",
    "Please confirm your identity",
    "This is a fraud alert call"
]

for i, text in enumerate(texts):
    tts.tts_to_file(
        text=text,
        file_path=os.path.join(output_dir, f"tts_{i}.wav")
    )

print("TTS dataset created")