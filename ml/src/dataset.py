import os
import torch
import librosa
import numpy as np
from torch.utils.data import Dataset

class AudioDataset(Dataset):
    def __init__(self, root_dir, sr=16000, duration=2):
        self.samples = []
        self.sr = sr
        self.max_len = sr * duration

        for label, class_name in enumerate(["real", "fake"]):
            class_dir = os.path.join(root_dir, class_name)

            for file in os.listdir(class_dir):
                if file.endswith(".wav") or file.endswith(".flac"):
                    path = os.path.join(class_dir, file)
                    self.samples.append((path, label))

        print(f"Loaded {len(self.samples)} samples from {root_dir}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]

        # =========================
        # LOAD AUDIO
        # =========================
        y, sr = librosa.load(path, sr=self.sr, mono=True)

        # =========================
        # FIX LENGTH (IMPORTANT)
        # =========================
        if len(y) < self.max_len:
            pad = self.max_len - len(y)
            y = np.pad(y, (0, pad))
        else:
            y = y[:self.max_len]

        # =========================
        # MEL SPECTROGRAM
        # =========================
        mel = librosa.feature.melspectrogram(
            y=y,
            sr=self.sr,
            n_mels=128,
            n_fft=1024,
            hop_length=512
        )

        mel = librosa.power_to_db(mel, ref=np.max)

        # =========================
        # NORMALIZE (CRITICAL)
        # =========================
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)

        # =========================
        # TO TENSOR
        # =========================
        mel = torch.tensor(mel).unsqueeze(0).float()  # (1, 128, T)
        label = torch.tensor(label).long()

        return mel, label