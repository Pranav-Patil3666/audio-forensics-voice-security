import torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torch.optim as optim
import os

from dataset import SpectrogramDataset
from model import CNNModel

BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"

csv_path = os.path.join(BASE, "features", "spectrograms", "labels.csv")

# Dataset
dataset = SpectrogramDataset(csv_path)

# Split dataset
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model
model = CNNModel().to(device)

# Loss & optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

# 🔥 Scheduler (IMPORTANT)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

# Training
EPOCHS = 20

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    # 🔹 Validation
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    accuracy = 100 * correct / total

    # 🔥 Step scheduler here
    scheduler.step()

    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.4f} | Val Acc: {accuracy:.2f}%")

# Save model
model_path = os.path.join(BASE, "models", "cnn_model.pth")
torch.save(model.state_dict(), model_path)

print("✅ Model training complete and saved")