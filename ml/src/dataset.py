import os
import torch
import librosa
import numpy as np

from torch.utils.data import Dataset


class AudioDataset(Dataset):

    def __init__(
        self,
        root_dir,
        sr=16000,
        duration=2,
        augment=False
    ):

        self.samples = []
        self.sr = sr
        self.max_len = sr * duration
        self.augment = augment

        for label, class_name in enumerate(["real", "fake"]):

            class_dir = os.path.join(
                root_dir,
                class_name
            )

            for file in os.listdir(class_dir):

                if file.endswith(".wav") or file.endswith(".flac"):

                    path = os.path.join(
                        class_dir,
                        file
                    )

                    self.samples.append(
                        (path, label)
                    )

        print(
            f"Loaded {len(self.samples)} samples "
            f"from {root_dir}"
        )

    def __len__(self):
        return len(self.samples)

    def apply_specaugment(self, mel):

         
        # TIME MASKING
         
        if np.random.rand() < 0.4:

            t = np.random.randint(4, 12)

            t0 = np.random.randint(
                0,
                max(1, mel.shape[1] - t)
            )

            mel[:, t0:t0 + t] = mel.mean()

         
        # FREQUENCY MASKING
         
        if np.random.rand() < 0.4:

            f = np.random.randint(4, 12)

            f0 = np.random.randint(
                0,
                max(1, mel.shape[0] - f)
            )

            mel[f0:f0 + f, :] = mel.mean()

        return mel

    def __getitem__(self, idx):

        path, label = self.samples[idx]

         
        # LOAD AUDIO
         
        y, sr = librosa.load(
            path,
            sr=self.sr,
            mono=True
        )

         
        # FIX LENGTH
         
        if len(y) < self.max_len:

            pad = self.max_len - len(y)

            y = np.pad(
                y,
                (0, pad)
            )

        else:

            y = y[:self.max_len]

         
        # MEL SPECTROGRAM
         
        mel = librosa.feature.melspectrogram(
            y=y,
            sr=self.sr,
            n_mels=128,
            n_fft=1024,
            hop_length=512
        )

        mel = librosa.power_to_db(
            mel,
            ref=np.max
        )

         
        # NORMALIZATION
         
        mel = (
            mel - mel.mean()
        ) / (
            mel.std() + 1e-6
        )

         
        # SPEC AUGMENT
         
        if self.augment:
            mel = self.apply_specaugment(mel)

         
        # TO TENSOR
         
        mel = torch.tensor(
            mel
        ).unsqueeze(0).float()

        label = torch.tensor(
            label
        ).long()

        return mel, label