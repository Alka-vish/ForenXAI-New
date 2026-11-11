
"""
ForenXAI AI-Generated Image Detection Service

Active models:
1. umm-maybe/AI-image-detector (pretrained Swin Transformer)
2. forensic_cnn_tinygenimage_best.pth (AI-generated image classifier)
3. forensic_cnn_casia_tamper_best.pth (tampering classifier)

The Face detector implementation is retained, but it is not used by
the active detection flow.

Model outputs are statistical evidence, not definitive forensic proof.
"""

import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageOps
from torchvision import transforms


# ==========================================================
# CONFIGURATION
# ==========================================================

MODEL_ID = "umm-maybe/AI-image-detector"
FACE_MODEL_ID = "SadraCoding/SDXL-Deepfake-Detector"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# This file is expected at forensic-engine/services/ai_detector.py
ENGINE_DIR = Path(__file__).resolve().parent.parent

# Support either forensic-engine/models or a models folder
# alongside forensic-engine.
MODEL_DIR_CANDIDATES = [
    ENGINE_DIR / "models",
    ENGINE_DIR.parent / "models",
]

GENIMAGE_CHECKPOINT = "forensic_cnn_tinygenimage_best.pth"
CASIA_CHECKPOINT = "forensic_cnn_casia_tamper_best.pth"

IMAGE_SIZE = 224

LOCAL_TRANSFORM = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

_model_lock = threading.Lock()

_model = None
_processor = None
_load_error: Optional[str] = None
_model_initialized = False

# Retained for compatibility, but not used in active inference.
_face_model = None
_face_processor = None
_face_load_error: Optional[str] = None
_face_model_initialized = False

_genimage_model = None
_genimage_load_error: Optional[str] = None
_genimage_initialized = False

_casia_model = None
_casia_load_error: Optional[str] = None
_casia_initialized = False


# ==========================================================
# LOCAL FORENSIC CNN ARCHITECTURE
# Must match the architecture used during training.
# ==========================================================

def create_srm_filters():
    """Create the seven fixed SRM-inspired filters used during training."""
    filters = [
        np.array([
            [0, 0, 0],
            [0, -1, 1],
            [0, 0, 0],
        ], dtype=np.float32),

        np.array([
            [0, 0, 0],
            [0, -1, 0],
            [0, 1, 0],
        ], dtype=np.float32),

        np.array([
            [0, 0, 0],
            [-1, 0, 1],
            [0, 0, 0],
        ], dtype=np.float32),

        np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0],
        ], dtype=np.float32),

        np.array([
            [-1, 2, -1],
            [2, -4, 2],
            [-1, 2, -1],
        ], dtype=np.float32),

        np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1],
        ], dtype=np.float32),

        np.array([
            [1, -2, 1],
            [-2, 4, -2],
            [1, -2, 1],
        ], dtype=np.float32),
    ]

    kernels = np.stack(filters)
    kernels = np.repeat(kernels[:, None, :, :], 3, axis=1)
    return torch.tensor(kernels, dtype=torch.float32)


class ForensicFeatures(nn.Module):
    def __init__(self):
        super().__init__()

        srm = create_srm_filters()

        self.srm = nn.Conv2d(
            in_channels=3,
            out_channels=7,
            kernel_size=3,
            padding=1,
            bias=False,
        )

        with torch.no_grad():
            self.srm.weight.copy_(srm)

        self.srm.weight.requires_grad = False
        self.bn_srm = nn.BatchNorm2d(7)

    def fft_features(self, x):
        gray = (
            0.299 * x[:, 0:1]
            + 0.587 * x[:, 1:2]
            + 0.114 * x[:, 2:3]
        )

        fft = torch.fft.fft2(gray)
        magnitude = torch.log1p(torch.abs(fft))
        magnitude = torch.fft.fftshift(magnitude, dim=(-2, -1))

        mean = magnitude.mean(dim=(-2, -1), keepdim=True)
        std = magnitude.std(dim=(-2, -1), keepdim=True) + 1e-6

        return (magnitude - mean) / std

    def wavelet_features(self, x):
        gray = (
            0.299 * x[:, 0:1]
            + 0.587 * x[:, 1:2]
            + 0.114 * x[:, 2:3]
        )

        h, w = gray.shape[-2:]
        h -= h % 2
        w -= w % 2
        gray = gray[:, :, :h, :w]

        x00 = gray[:, :, 0::2, 0::2]
        x01 = gray[:, :, 0::2, 1::2]
        x10 = gray[:, :, 1::2, 0::2]
        x11 = gray[:, :, 1::2, 1::2]

        ll = (x00 + x01 + x10 + x11) / 2.0
        lh = (x00 - x01 + x10 - x11) / 2.0
        hl = (x00 + x01 - x10 - x11) / 2.0
        hh = (x00 - x01 - x10 + x11) / 2.0

        return torch.cat([ll, lh, hl, hh], dim=1)

    def forward(self, x):
        srm = self.bn_srm(self.srm(x))
        fft = self.fft_features(x)
        wavelet = self.wavelet_features(x)
        return srm, fft, wavelet


class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels, out_channels,
                kernel_size=3, padding=1, bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels, out_channels,
                kernel_size=3, padding=1, bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.MaxPool2d(2),
        )

    def forward(self, x):
        return self.block(x)


class ForensicCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.features = ForensicFeatures()

        self.srm_branch = nn.Sequential(
            ConvBlock(7, 32),
            ConvBlock(32, 64),
            ConvBlock(64, 128),
        )

        self.fft_branch = nn.Sequential(
            ConvBlock(1, 32),
            ConvBlock(32, 64),
            ConvBlock(64, 128),
        )

        self.wavelet_branch = nn.Sequential(
            ConvBlock(4, 32),
            ConvBlock(32, 64),
            ConvBlock(64, 128),
        )

        self.fusion = nn.Sequential(
            nn.Linear(128 * 3, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        srm, fft, wavelet = self.features(x)

        srm_features = F.adaptive_avg_pool2d(
            self.srm_branch(srm), 1
        ).flatten(1)

        fft_features = F.adaptive_avg_pool2d(
            self.fft_branch(fft), 1
        ).flatten(1)

        wavelet_features = F.adaptive_avg_pool2d(
            self.wavelet_branch(wavelet), 1
        ).flatten(1)

        fused = torch.cat(
            [srm_features, fft_features, wavelet_features],
            dim=1,
        )

        return self.fusion(fused)


# ==========================================================
# CHECKPOINT HELPERS
# ==========================================================

def _find_checkpoint(filename: str) -> Path:
    for directory in MODEL_DIR_CANDIDATES:
        candidate = directory / filename
        if candidate.is_file():
            return candidate

    searched = ", ".join(
        str(directory / filename)
        for directory in MODEL_DIR_CANDIDATES
    )
    raise FileNotFoundError(
        f"Checkpoint not found. Searched: {searched}"
    )


def _load_local_cnn(filename: str):
    checkpoint_path = _find_checkpoint(filename)

    # Checkpoints are assumed to be trusted files produced by your
    # own training script. Load them only from your local project.
    try:
        checkpoint = torch.load(
            checkpoint_path,
            map_location=DEVICE,
            weights_only=True,
        )
    except TypeError:
        # Compatibility with older PyTorch versions.
        checkpoint = torch.load(
            checkpoint_path,
            map_location=DEVICE,
        )

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

    model = ForensicCNN()
    model.load_state_dict(state_dict, strict=True)
    model.to(DEVICE)
    model.eval()

    print(f"Loaded local model: {checkpoint_path}")
    return model


def get_genimage_model():
    global _genimage_model, _genimage_load_error, _genimage_initialized

    if _genimage_initialized:
        return _genimage_model, _genimage_load_error

    with _model_lock:
        if not _genimage_initialized:
            try:
                _genimage_model = _load_local_cnn(GENIMAGE_CHECKPOINT)
            except Exception as exc:
                _genimage_load_error = str(exc)
                print("GenImage CNN loading failed:", _genimage_load_error)
            finally:
                _genimage_initialized = True

    return _genimage_model, _genimage_load_error


def get_casia_model():
    global _casia_model, _casia_load_error, _casia_initialized

    if _casia_initialized:
        return _casia_model, _casia_load_error

    with _model_lock:
        if not _casia_initialized:
            try:
                _casia_model = _load_local_cnn(CASIA_CHECKPOINT)
            except Exception as exc:
                _casia_load_error = str(exc)
                print("CASIA CNN loading failed:", _casia_load_error)
            finally:
                _casia_initialized = True

    return _casia_model, _casia_load_error


# ==========================================================
# PRETRAINED SWIN MODEL
# ==========================================================

def get_ai_detector():
    global _model, _processor, _load_error, _model_initialized

    if _model_initialized:
        return _processor, _model, _load_error

    with _model_lock:
        if not _model_initialized:
            try:
                from transformers import (
                    AutoImageProcessor,
                    AutoModelForImageClassification,
                )

                _processor = AutoImageProcessor.from_pretrained(MODEL_ID)
                _model = AutoModelForImageClassification.from_pretrained(
                    MODEL_ID
                )
                _model.to(DEVICE)
                _model.eval()

                print("Loaded pretrained detector:", MODEL_ID)
                print("Pretrained labels:", _model.config.id2label)

            except Exception as exc:
                _load_error = str(exc)
                _processor = None
                _model = None
                print("Pretrained detector loading failed:", _load_error)

            finally:
                _model_initialized = True

    return _processor, _model, _load_error


# ==========================================================
# RETAINED FACE MODEL LOADER
# Not called by detect_ai_generated_image().
# ==========================================================

def get_face_detector():
    global _face_model, _face_processor
    global _face_load_error, _face_model_initialized

    if _face_model_initialized:
        return _face_processor, _face_model, _face_load_error

    with _model_lock:
        if not _face_model_initialized:
            try:
                from transformers import (
                    AutoImageProcessor,
                    AutoModelForImageClassification,
                )

                _face_processor = AutoImageProcessor.from_pretrained(
                    FACE_MODEL_ID
                )
                _face_model = AutoModelForImageClassification.from_pretrained(
                    FACE_MODEL_ID
                )
                _face_model.to(DEVICE)
                _face_model.eval()

            except Exception as exc:
                _face_load_error = str(exc)
                _face_processor = None
                _face_model = None
                print("Face detector loading failed:", _face_load_error)

            finally:
                _face_model_initialized = True

    return _face_processor, _face_model, _face_load_error


# ==========================================================
# IMAGE CROPS
# ==========================================================

def create_image_crops(image: Image.Image) -> List[Image.Image]:
    image = image.convert("RGB")
    width, height = image.size

    crop_width = max(1, min(int(width * 0.75), width))
    crop_height = max(1, min(int(height * 0.75), height))

    left = (width - crop_width) // 2
    top = (height - crop_height) // 2

    return [
        image,
        image.crop((
            left, top, left + crop_width, top + crop_height
        )),
        image.crop((0, 0, crop_width, crop_height)),
        image.crop((
            width - crop_width, 0, width, crop_height
        )),
        image.crop((
            (width - crop_width) // 2,
            height - crop_height,
            (width - crop_width) // 2 + crop_width,
            height,
        )),
    ]


# ==========================================================
# PRETRAINED MODEL INFERENCE
# ==========================================================

def run_single_inference(
    image: Image.Image,
    processor,
    model,
) -> Dict[str, float]:
    inputs = processor(
        images=image.convert("RGB"),
        return_tensors="pt",
    )

    inputs = {key: value.to(DEVICE) for key, value in inputs.items()}

    with torch.inference_mode():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=1)[0]

    labels = getattr(model.config, "id2label", {})
    labels = {
        int(index): str(label).lower()
        for index, label in labels.items()
    }

    artificial_index = None
    human_index = None

    for index, label in labels.items():
        if label in {
            "artificial", "fake", "ai", "generated", "synthetic"
        }:
            artificial_index = index
        elif label in {"human", "real", "authentic"}:
            human_index = index

    if artificial_index is None or human_index is None:
        raise ValueError(
            f"Cannot identify artificial/human labels: {labels}"
        )

    return {
        "artificial": float(probabilities[artificial_index].item()),
        "human": float(probabilities[human_index].item()),
    }


def run_pretrained_detector(image, processor, model):
    artificial_scores = []
    human_scores = []
    crop_results = []

    for index, crop in enumerate(create_image_crops(image)):
        original = run_single_inference(crop, processor, model)
        flipped = run_single_inference(ImageOps.mirror(crop), processor, model)

        artificial = (original["artificial"] + flipped["artificial"]) / 2
        human = (original["human"] + flipped["human"]) / 2

        artificial_scores.append(artificial)
        human_scores.append(human)

        crop_results.append({
            "crop_index": index,
            "original_artificial": round(original["artificial"], 4),
            "flipped_artificial": round(flipped["artificial"], 4),
            "average_artificial": round(artificial, 4),
            "average_human": round(human, 4),
        })

    ai_score = sum(artificial_scores) / len(artificial_scores)
    human_score = sum(human_scores) / len(human_scores)
    total = ai_score + human_score

    if total > 0:
        ai_score /= total
        human_score /= total

    return ai_score, human_score, crop_results


# ==========================================================
# LOCAL CNN INFERENCE
# ==========================================================

def run_local_cnn(image: Image.Image, model):
    tensor = LOCAL_TRANSFORM(image.convert("RGB")).unsqueeze(0).to(DEVICE)

    with torch.inference_mode():
        logit = model(tensor)
        score = torch.sigmoid(logit).reshape(-1)[0].item()

    return float(score)


# ==========================================================
# MAIN DETECTION FUNCTION
# ==========================================================

def detect_ai_generated_image(
    pil_image: Image.Image,
) -> Dict[str, Any]:
    """
    Run the pretrained detector and both local CNN checkpoints.

    GenImage checkpoint:
        Class 1 is assumed to mean AI-generated.

    CASIA checkpoint:
        Class 1 is assumed to mean tampered.

    Verify those class mappings against the datasets used for training.
    CASIA output is reported separately and is NOT blended into the
    AI-generation probability.
    """

    if pil_image is None:
        return {
            "status": "error",
            "model_name": MODEL_ID,
            "message": "No image was provided.",
            "prediction": None,
            "model_score": None,
            "confidence_scores": None,
        }

    image = pil_image.convert("RGB")

    # ------------------------------------------------------
    # Load models independently so one unavailable model
    # does not prevent the others from running.
    # ------------------------------------------------------

    processor, swin_model, swin_error = get_ai_detector()
    genimage_model, genimage_error = get_genimage_model()
    casia_model, casia_error = get_casia_model()

    swin_ai = None
    swin_human = None
    crop_results = []
    inference_errors = {}

    if processor is not None and swin_model is not None:
        try:
            swin_ai, swin_human, crop_results = run_pretrained_detector(
                image, processor, swin_model
            )
        except Exception as exc:
            inference_errors["pretrained_detector"] = str(exc)
    else:
        inference_errors["pretrained_detector"] = (
            swin_error or "Pretrained detector unavailable."
        )

    genimage_ai = None
    if genimage_model is not None:
        try:
            genimage_ai = run_local_cnn(image, genimage_model)
        except Exception as exc:
            inference_errors["genimage_cnn"] = str(exc)
    else:
        inference_errors["genimage_cnn"] = (
            genimage_error or "GenImage checkpoint unavailable."
        )

    casia_tamper = None
    if casia_model is not None:
        try:
            casia_tamper = run_local_cnn(image, casia_model)
        except Exception as exc:
            inference_errors["casia_cnn"] = str(exc)
    else:
        inference_errors["casia_cnn"] = (
            casia_error or "CASIA checkpoint unavailable."
        )

    # ------------------------------------------------------
    # AI-generation ensemble
    #
    # If both AI detectors are available, use a provisional
    # 50/50 blend. If only one is available, use that model.
    # These weights are experimental, not calibrated.
    # ------------------------------------------------------

    available_ai_scores = []

    if swin_ai is not None:
        available_ai_scores.append(("swin", swin_ai))

    if genimage_ai is not None:
        available_ai_scores.append(("genimage", genimage_ai))

    if not available_ai_scores:
        return {
            "status": "unavailable",
            "model_name": MODEL_ID,
            "model_architecture": "Swin Transformer + local forensic CNN",
            "message": "No AI-generation detector completed inference.",
            "prediction": None,
            "model_score": None,
            "confidence_scores": None,
            "general_model_scores": None,
            "local_model_scores": {
                "genimage_ai_probability": None,
                "casia_tamper_probability": casia_tamper,
            },
            "crop_results": crop_results,
            "inference_errors": inference_errors,
            "forensic_notice": (
                "No AI-generation probability was produced. "
                "CASIA tampering output, if available, is separate."
            ),
        }

    if len(available_ai_scores) == 2:
        ensemble_ai = (swin_ai + genimage_ai) / 2
        ensemble_type = "swin_50_percent_genimage_50_percent"
    else:
        ensemble_ai = available_ai_scores[0][1]
        ensemble_type = f"{available_ai_scores[0][0]}_only"

    ensemble_ai = max(0.0, min(1.0, float(ensemble_ai)))
    ensemble_human = 1.0 - ensemble_ai

    if ensemble_ai >= 0.5:
        prediction = "artificial"
    else:
        prediction = "human"

    difference = abs(ensemble_ai - ensemble_human)

    if difference < 0.20:
        interpretation = "uncertain"
    elif prediction == "artificial":
        interpretation = "artificial_signal"
    else:
        interpretation = "human_signal"

    return {
        "status": "success",
        "model_name": MODEL_ID,
        "model_architecture": "Swin Transformer + ForensicCNN",
        "prediction": prediction,
        "model_score": round(ensemble_ai, 4),
        "confidence_scores": {
            "artificial": round(ensemble_ai, 4),
            "human": round(ensemble_human, 4),
        },
        "general_model_scores": (
            {
                "artificial": round(swin_ai, 4),
                "human": round(swin_human, 4),
            }
            if swin_ai is not None
            else None
        ),
        "local_model_scores": {
            "genimage_ai_probability": (
                round(genimage_ai, 4)
                if genimage_ai is not None
                else None
            ),
            "casia_tamper_probability": (
                round(casia_tamper, 4)
                if casia_tamper is not None
                else None
            ),
        },
        "face_model_scores": None,
        "ensemble_type": ensemble_type,
        "interpretation": interpretation,
        "score_difference": round(difference, 4),
        "crop_results": crop_results,
        "face_crop_results": [],
        "score_interpretation": {
            "artificial": (
                "Estimated AI-generation probability from available "
                "AI-generation detectors; not proof of synthetic origin."
            ),
            "human": (
                "Complement of the ensemble AI-generation score."
            ),
            "genimage_ai_probability": (
                "Sigmoid output from the local GenImage CNN. "
                "Assumes class 1 represents AI-generated images."
            ),
            "casia_tamper_probability": (
                "Sigmoid output from the local CASIA CNN. "
                "Assumes class 1 represents tampered images; "
                "not an AI-generation probability."
            ),
        },
        "forensic_notice": (
            "Model outputs are statistical indicators, not definitive "
            "proof. Interpret them alongside the forensic evidence ledger."
        ),
        "limitations": [
            "The ensemble weights are experimental and not calibrated.",
            "Checkpoint class mappings must match the training labels.",
            "CASIA tampering output is not included in the AI-generation score.",
            "Compression, resizing, post-processing, and dataset bias may affect results.",
            "Predictions are not definitive forensic proof.",
        ],
        "inference_errors": inference_errors,
    }
