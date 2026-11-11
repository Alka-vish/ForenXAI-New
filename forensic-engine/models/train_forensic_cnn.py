import os
import math
import random
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from datasets import load_dataset
from PIL import Image
from torchvision import transforms


# ============================================================
# CONFIG
# ============================================================

DATASET_NAME = "TheKernel01/Tiny-GenImage"

IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 1e-4
NUM_WORKERS = 4

CHECKPOINT_DIR = "/home/forenxai-training/checkpoints"
RESULTS_DIR = "/home/forenxai-training/results"

os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("=" * 70)
print("FORENXAI FORENSIC CNN")
print("=" * 70)
print("Device:", DEVICE)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2), "GB")


# ============================================================
# SRM FILTERS
# ============================================================

def create_srm_filters():
    """
    Creates 7 fixed high-pass SRM-inspired filters.
    """

    filters = []

    filters.append(
        np.array([
            [0, 0, 0],
            [0, -1, 1],
            [0, 0, 0]
        ], dtype=np.float32)
    )

    filters.append(
        np.array([
            [0, 0, 0],
            [0, -1, 0],
            [0, 1, 0]
        ], dtype=np.float32)
    )

    filters.append(
        np.array([
            [0, 0, 0],
            [-1, 0, 1],
            [0, 0, 0]
        ], dtype=np.float32)
    )

    filters.append(
        np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ], dtype=np.float32)
    )

    filters.append(
        np.array([
            [-1, 2, -1],
            [2, -4, 2],
            [-1, 2, -1]
        ], dtype=np.float32)
    )

    filters.append(
        np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ], dtype=np.float32)
    )

    filters.append(
        np.array([
            [1, -2, 1],
            [-2, 4, -2],
            [1, -2, 1]
        ], dtype=np.float32)
    )

    kernels = np.stack(filters)

    # Apply same filter to RGB channels
    kernels = np.repeat(kernels[:, None, :, :], 3, axis=1)

    return torch.tensor(kernels, dtype=torch.float32)


# ============================================================
# FORENSIC FEATURE EXTRACTION
# ============================================================

class ForensicFeatures(nn.Module):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # SRM
        # ----------------------------------------------------

        srm = create_srm_filters()

        self.srm = nn.Conv2d(
            in_channels=3,
            out_channels=7,
            kernel_size=3,
            padding=1,
            bias=False
        )

        with torch.no_grad():
            self.srm.weight.copy_(srm)

        # SRM filters remain fixed
        self.srm.weight.requires_grad = False

        # ----------------------------------------------------
        # Feature normalization
        # ----------------------------------------------------

        self.bn_srm = nn.BatchNorm2d(7)

    # --------------------------------------------------------
    # FFT
    # --------------------------------------------------------

    def fft_features(self, x):

        gray = (
            0.299 * x[:, 0:1] +
            0.587 * x[:, 1:2] +
            0.114 * x[:, 2:3]
        )

        fft = torch.fft.fft2(gray)

        magnitude = torch.abs(fft)

        magnitude = torch.log1p(magnitude)

        magnitude = torch.fft.fftshift(magnitude, dim=(-2, -1))

        # Normalize each image
        mean = magnitude.mean(dim=(-2, -1), keepdim=True)
        std = magnitude.std(dim=(-2, -1), keepdim=True) + 1e-6

        magnitude = (magnitude - mean) / std

        return magnitude

    # --------------------------------------------------------
    # Haar Wavelet
    # --------------------------------------------------------

    def wavelet_features(self, x):

        # Convert RGB to grayscale
        gray = (
            0.299 * x[:, 0:1] +
            0.587 * x[:, 1:2] +
            0.114 * x[:, 2:3]
        )

        # Make dimensions even
        h = gray.shape[-2]
        w = gray.shape[-1]

        h = h - (h % 2)
        w = w - (w % 2)

        gray = gray[:, :, :h, :w]

        x00 = gray[:, :, 0::2, 0::2]
        x01 = gray[:, :, 0::2, 1::2]
        x10 = gray[:, :, 1::2, 0::2]
        x11 = gray[:, :, 1::2, 1::2]

        # Haar components
        LL = (x00 + x01 + x10 + x11) / 2.0

        LH = (x00 - x01 + x10 - x11) / 2.0

        HL = (x00 + x01 - x10 - x11) / 2.0

        HH = (x00 - x01 - x10 + x11) / 2.0

        return torch.cat([LL, LH, HL, HH], dim=1)

    # --------------------------------------------------------
    # Forward
    # --------------------------------------------------------

    def forward(self, x):

        srm = self.srm(x)
        srm = self.bn_srm(srm)

        fft = self.fft_features(x)

        wavelet = self.wavelet_features(x)

        return srm, fft, wavelet


# ============================================================
# CNN BRANCH
# ============================================================

class ConvBlock(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True),

            nn.MaxPool2d(2)
        )

    def forward(self, x):
        return self.block(x)


# ============================================================
# FORENSIC CNN
# ============================================================

class ForensicCNN(nn.Module):

    def __init__(self):

        super().__init__()

        self.features = ForensicFeatures()

        # ----------------------------------------------------
        # SRM branch
        # ----------------------------------------------------

        self.srm_branch = nn.Sequential(

            ConvBlock(7, 32),

            ConvBlock(32, 64),

            ConvBlock(64, 128)
        )

        # ----------------------------------------------------
        # FFT branch
        # ----------------------------------------------------

        self.fft_branch = nn.Sequential(

            ConvBlock(1, 32),

            ConvBlock(32, 64),

            ConvBlock(64, 128)
        )

        # ----------------------------------------------------
        # Wavelet branch
        # ----------------------------------------------------

        self.wavelet_branch = nn.Sequential(

            ConvBlock(4, 32),

            ConvBlock(32, 64),

            ConvBlock(64, 128)
        )

        # ----------------------------------------------------
        # Fusion
        # ----------------------------------------------------

        self.fusion = nn.Sequential(

            nn.Linear(128 * 3, 256),

            nn.BatchNorm1d(256),

            nn.ReLU(inplace=True),

            nn.Dropout(0.4),

            nn.Linear(256, 64),

            nn.ReLU(inplace=True),

            nn.Dropout(0.3),

            nn.Linear(64, 1)
        )

    def forward(self, x):

        srm, fft, wavelet = self.features(x)

        srm_features = self.srm_branch(srm)

        fft_features = self.fft_branch(fft)

        wavelet_features = self.wavelet_branch(wavelet)

        # Global average pooling
        srm_features = F.adaptive_avg_pool2d(
            srm_features, 1
        ).flatten(1)

        fft_features = F.adaptive_avg_pool2d(
            fft_features, 1
        ).flatten(1)

        wavelet_features = F.adaptive_avg_pool2d(
            wavelet_features, 1
        ).flatten(1)

        # Combine all forensic representations
        fused = torch.cat(
            [
                srm_features,
                fft_features,
                wavelet_features
            ],
            dim=1
        )

        output = self.fusion(fused)

        return output


# ============================================================
# DATASET
# ============================================================

class TinyGenImageDataset(Dataset):

    def __init__(self, hf_dataset, transform=None):

        self.dataset = hf_dataset
        self.transform = transform

    def __len__(self):

        return len(self.dataset)

    def __getitem__(self, index):

        item = self.dataset[index]

        image = item["image"]
        label = item["label"]

        if not isinstance(image, Image.Image):
            image = Image.fromarray(np.array(image))

        image = image.convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(
            label,
            dtype=torch.float32
        )


# ============================================================
# TRANSFORMS
# ============================================================

train_transform = transforms.Compose([

    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.RandomHorizontalFlip(),

    transforms.RandomApply(
        [
            transforms.RandomRotation(5)
        ],
        p=0.3
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


val_transform = transforms.Compose([

    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading Tiny-GenImage...")

dataset = load_dataset(
    DATASET_NAME
)

train_dataset = TinyGenImageDataset(
    dataset["train"],
    train_transform
)

val_dataset = TinyGenImageDataset(
    dataset["validation"],
    val_transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS,
    pin_memory=True,
    persistent_workers=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
    pin_memory=True,
    persistent_workers=True
)

print("Training images:", len(train_dataset))
print("Validation images:", len(val_dataset))


# ============================================================
# MODEL
# ============================================================

model = ForensicCNN().to(DEVICE)

criterion = nn.BCEWithLogitsLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=1e-4
)

scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer,
    T_max=EPOCHS
)


# ============================================================
# TRAINING
# ============================================================

def train_one_epoch():

    model.train()

    total_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (images, labels) in enumerate(train_loader):

        images = images.to(
            DEVICE,
            non_blocking=True
        )

        labels = labels.to(
            DEVICE,
            non_blocking=True
        ).unsqueeze(1)

        optimizer.zero_grad(set_to_none=True)

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        total_loss += loss.item() * images.size(0)

        predictions = (
            torch.sigmoid(outputs) >= 0.5
        ).float()

        correct += (
            predictions == labels
        ).sum().item()

        total += labels.size(0)

        if (batch_idx + 1) % 100 == 0:

            print(
                f"  Batch {batch_idx + 1}/{len(train_loader)} "
                f"Loss: {loss.item():.4f}"
            )

    return (
        total_loss / total,
        correct / total
    )


# ============================================================
# VALIDATION
# ============================================================

@torch.no_grad()
def validate():

    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    all_probs = []
    all_labels = []

    for images, labels in val_loader:

        images = images.to(
            DEVICE,
            non_blocking=True
        )

        labels = labels.to(
            DEVICE,
            non_blocking=True
        ).unsqueeze(1)

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        probabilities = torch.sigmoid(
            outputs
        )

        predictions = (
            probabilities >= 0.5
        ).float()

        total_loss += loss.item() * images.size(0)

        correct += (
            predictions == labels
        ).sum().item()

        total += labels.size(0)

        all_probs.extend(
            probabilities.squeeze(1).cpu().numpy()
        )

        all_labels.extend(
            labels.squeeze(1).cpu().numpy()
        )

    accuracy = correct / total

    return (
        total_loss / total,
        accuracy,
        np.array(all_probs),
        np.array(all_labels)
    )


# ============================================================
# TRAIN
# ============================================================

best_accuracy = 0.0

print("\n" + "=" * 70)
print("STARTING TRAINING")
print("=" * 70)

for epoch in range(EPOCHS):

    print(
        f"\nEpoch {epoch + 1}/{EPOCHS}"
    )

    train_loss, train_accuracy = train_one_epoch()

    val_loss, val_accuracy, _, _ = validate()

    scheduler.step()

    print(
        f"Train Loss: {train_loss:.4f} | "
        f"Train Accuracy: {train_accuracy * 100:.2f}%"
    )

    print(
        f"Val Loss: {val_loss:.4f} | "
        f"Val Accuracy: {val_accuracy * 100:.2f}%"
    )

    # Save best model
    if val_accuracy > best_accuracy:

        best_accuracy = val_accuracy

        checkpoint_path = os.path.join(
            CHECKPOINT_DIR,
            "forensic_cnn_tinygenimage_best.pth"
        )

        torch.save(
            {
                "epoch": epoch + 1,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_accuracy": val_accuracy,
                "image_size": IMAGE_SIZE
            },
            checkpoint_path
        )

        print(
            "✓ Best model saved:",
            checkpoint_path
        )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)

print(
    f"Best validation accuracy: "
    f"{best_accuracy * 100:.2f}%"
)

print(
    "Checkpoint:",
    os.path.join(
        CHECKPOINT_DIR,
        "forensic_cnn_tinygenimage_best.pth"
    )
)
