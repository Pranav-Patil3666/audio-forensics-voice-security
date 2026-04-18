import torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torch.optim as optim
import os
import random
import numpy as np

from dataset import SpectrogramDataset
from model import CNNModel


def main():
    BASE = r"D:\ml-project\Audio Forensics for Voice Security\ml"
    csv_path = os.path.join(BASE, "features", "spectrograms", "labels.csv")

    # =========================
    # REPRODUCIBILITY
    # =========================
    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)

    # =========================
    # DATASET
    # =========================
    dataset = SpectrogramDataset(csv_path)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(
        train_dataset,
        batch_size=32,
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=32,
        num_workers=2,
        pin_memory=True
    )

    # =========================
    # DEVICE
    # =========================
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # =========================
    # MODEL
    # =========================
    model = CNNModel().to(device)

    # =========================
    # LOSS
    # =========================
    criterion = nn.CrossEntropyLoss()

    # =========================
    # OPTIMIZER
    # =========================
    optimizer = optim.Adam(
        model.parameters(),
        lr=0.001,
        weight_decay=1e-4
    )

    # =========================
    # LR SCHEDULER
    # =========================
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=5,
        gamma=0.5
    )

    # =========================
    # TRAINING LOOP
    # =========================
    EPOCHS = 20
    best_acc = 0.0

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)

        # =========================
        # VALIDATION
        # =========================
        model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                _, predicted = torch.max(outputs, 1)

                correct += (predicted == labels).sum().item()
                total += labels.size(0)

        accuracy = 100 * correct / total

        # =========================
        # SAVE BEST MODEL
        # =========================
        if accuracy > best_acc:
            best_acc = accuracy
            torch.save(
                model.state_dict(),
                os.path.join(BASE, "models", "cnn_model_best.pth")
            )

        scheduler.step()

        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.4f} | Val Acc: {accuracy:.2f}%")

    # =========================
    # FINAL SAVE
    # =========================
    torch.save(
        model.state_dict(),
        os.path.join(BASE, "models", "cnn_model_last.pth")
    )

    print(f"✅ Training complete | Best Acc: {best_acc:.2f}%")


# =========================
# WINDOWS FIX (CRITICAL)
# =========================
if __name__ == "__main__":
    main()