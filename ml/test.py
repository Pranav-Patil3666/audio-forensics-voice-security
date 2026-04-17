from TTS.api import TTS

print("Loading model...")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

print("Generating audio...")
tts.tts_to_file(
    text="This is a test of synthetic voice generation",
    file_path="test_tts.wav"
)

print("DONE")