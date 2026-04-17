import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image
from torchvision import transforms


class SpectrogramDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)

        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        img_path = row["path"]
        label = row["label"]

        image = Image.open(img_path).convert("L")  # grayscale

        image = self.transform(image)

        return image, torch.tensor(label, dtype=torch.long)