from TTS.api import TTS
import os

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

hindi_dir = os.path.join(BASE, "data", "real", "hindi")

files = os.listdir(hindi_dir)

if len(files) == 0:
    raise Exception("❌ Hindi dataset folder is empty")

# pick first valid file
input_audio = None
for f in files:
    if f.endswith(".wav") or f.endswith(".mp3"):
        input_audio = os.path.join(hindi_dir, f)
        break

if input_audio is None:
    raise Exception("❌ No valid audio file found")

print("Using:", input_audio)

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

output_dir = os.path.join(BASE, "data", "fake", "cloned")
os.makedirs(output_dir, exist_ok=True)

tts.tts_to_file(
    text="This is a cloned version of your voice",
    speaker_wav=input_audio,
    file_path=os.path.join(output_dir, "clone_0.wav")
)

print("Cloned dataset created")