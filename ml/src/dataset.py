import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image
from torchvision import transforms
import os


class SpectrogramDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)

        # Pre-extract columns (faster than iloc every time)
        self.paths = self.data["path"].values
        self.labels = self.data["label"].values

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        img_path = self.paths[idx]
        label = int(self.labels[idx])

        try:
            image = Image.open(img_path).convert("L")
        except Exception:
            # 🔥 fallback (very important for stability)
            # create dummy image instead of crashing
            image = Image.new("L", (224, 224))

        image = self.transform(image)

        return image, torch.tensor(label, dtype=torch.long)