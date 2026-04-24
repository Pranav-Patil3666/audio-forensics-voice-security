import webrtcvad
import numpy as np


vad = webrtcvad.Vad(2)  # aggressiveness: 0–3 (2 is balanced)


def is_speech(audio, sr):
    """
    audio: numpy array (float)
    sr: sample rate (should be 16000)
    """

    # convert float [-1,1] → int16
    audio_int16 = (audio * 32767).astype(np.int16)

    frame_duration = 30  # ms
    frame_size = int(sr * frame_duration / 1000)

    speech_frames = 0
    total_frames = 0

    for i in range(0, len(audio_int16) - frame_size, frame_size):
        frame = audio_int16[i:i + frame_size]

        try:
            if vad.is_speech(frame.tobytes(), sr):
                speech_frames += 1
        except:
            continue

        total_frames += 1

    if total_frames == 0:
        return False

    speech_ratio = speech_frames / total_frames

    # threshold (tune later)
    return speech_ratio > 0.3