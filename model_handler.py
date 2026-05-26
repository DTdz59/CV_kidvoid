import io
import json
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image, ImageFilter, ImageOps
from skimage.feature import hog


FRUIT_LABELS = ["apple", "banana", "grape", "orange", "pomegranate"]
PREPROCESSING_STEPS = ["exif_transpose", "rgb_convert", "autocontrast", "sharpen"]

TRANSFORM_IMAGENET = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

TRANSFORM_FRUIT_RESNET = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])


class ELM:
    def __init__(self, n_hidden=4096, C=500.0, activation="relu"):
        self.n_hidden = n_hidden
        self.C = C
        self.activation = activation
        self.W = self.b = self.beta = None

    def _h(self, X):
        H = X @ self.W + self.b
        if self.activation == "relu":
            return np.maximum(0, H)
        if self.activation == "sigmoid":
            return 1 / (1 + np.exp(-np.clip(H, -500, 500)))
        return np.tanh(H)

    def predict_proba_raw(self, X):
        scores = self._h(X) @ self.beta
        e = np.exp(scores - scores.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    def predict_proba_calibrated(self, X, temperature=0.5):
        proba = self.predict_proba_raw(X)
        log_p = np.log(proba + 1e-9) / temperature
        e = np.exp(log_p - log_p.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)


class ModelHandler:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.fruit_backbone = None
        self.fruit_elms = []
        self.sc_resnet = None
        self.sc_hog = None
        self.temperature = 1.0
        self.imagenet_model = None
        self.imagenet_cats = None
        self.vn_dict = {}
        self.keyword_map = {}
        self.fruit_ready = False
        self.imagenet_ready = False

    def load(self, model_dir="model", vn_dict_path="imagenet_vn.json"):
        try:
            self._load_fruit_model(Path(model_dir))
            self.fruit_ready = True
            print("Fruit model loaded (ResNet18 + HOG + ELM)")
        except FileNotFoundError:
            print("Fruit model artifacts not found; fruit branch disabled")
        except Exception as e:
            print(f"Fruit model error: {e}")

        weights = models.ResNet50_Weights.IMAGENET1K_V1
        resnet50 = models.resnet50(weights=weights)
        resnet50.eval()
        self.imagenet_model = resnet50
        self.imagenet_cats = weights.meta["categories"]
        self.imagenet_ready = True
        print("ImageNet model loaded (1000 classes)")

        with open(vn_dict_path, encoding="utf-8") as f:
            self.vn_dict = json.load(f)
        self.keyword_map = {
            k: [kw.lower() for kw in v.get("keywords", [])]
            for k, v in self.vn_dict.items()
        }
        print(f"VN dictionary: {len(self.vn_dict)} objects")

    def _build_fruit_resnet(self):
        model = models.resnet18(weights=None)
        for param in model.parameters():
            param.requires_grad = False
        model.fc = nn.Sequential(
            nn.Linear(model.fc.in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, len(FRUIT_LABELS)),
        )
        return model

    def _load_fruit_model(self, model_dir: Path):
        resnet_full = self._build_fruit_resnet()
        resnet_full.load_state_dict(
            torch.load(model_dir / "resnet_finetuned.pth", map_location=self.device)
        )

        backbone = models.resnet18(weights=None)
        backbone.fc = nn.Identity()
        ft_state = {
            k: v for k, v in resnet_full.state_dict().items()
            if not k.startswith("fc")
        }
        backbone.load_state_dict(ft_state, strict=False)
        self.fruit_backbone = backbone.to(self.device).eval()

        self.fruit_elms = []
        for i, act in enumerate(["relu", "tanh", "sigmoid"]):
            data = joblib.load(model_dir / f"elm_{i}_{act}.joblib")
            elm = ELM(
                n_hidden=data["n_hidden"],
                C=data["C"],
                activation=data["activation"],
            )
            elm.W = data["W"]
            elm.b = data["b"]
            elm.beta = data["beta"]
            self.fruit_elms.append(elm)

        self.sc_resnet = joblib.load(model_dir / "sc_resnet.joblib")
        self.sc_hog = joblib.load(model_dir / "sc_hog.joblib")
        self.temperature = joblib.load(model_dir / "temperature.joblib")["temperature"]

    def predict(self, image_bytes: bytes, mode: str = "imagenet") -> dict:
        raw_image = ImageOps.exif_transpose(
            Image.open(io.BytesIO(image_bytes))
        ).convert("RGB")
        quality = self._quality_report(raw_image)
        image = self._preprocess_image(raw_image)
        mode = mode if mode in {"fruit", "imagenet"} else "imagenet"

        if mode == "fruit":
            if not self.fruit_ready:
                raise RuntimeError("Fruit model is not ready")
            return {
                "source": "fruit",
                "mode": mode,
                "results": self._predict_fruit(image),
                "quality": quality,
                "preprocessing": PREPROCESSING_STEPS,
            }

        return {
            "source": "imagenet",
            "mode": mode,
            "results": self._predict_imagenet(image),
            "quality": quality,
            "preprocessing": PREPROCESSING_STEPS,
        }

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        image = ImageOps.autocontrast(image, cutoff=1)
        return image.filter(ImageFilter.SHARPEN)

    def _quality_report(self, image: Image.Image) -> dict:
        gray = image.convert("L").resize((256, 256))
        arr = np.asarray(gray, dtype=np.float32)

        brightness = float(arr.mean())
        contrast = float(arr.std())
        center = arr[1:-1, 1:-1]
        laplacian = (
            arr[:-2, 1:-1] + arr[2:, 1:-1] +
            arr[1:-1, :-2] + arr[1:-1, 2:] -
            4 * center
        )
        sharpness = float(laplacian.var())

        issues = []
        if brightness < 45:
            issues.append("dark")
        elif brightness > 215:
            issues.append("too_bright")
        if contrast < 18:
            issues.append("low_contrast")
        if sharpness < 80:
            issues.append("blurry")

        return {
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "sharpness": round(sharpness, 2),
            "issues": issues,
            "is_good": len(issues) == 0,
        }

    def _predict_fruit(self, image: Image.Image) -> list[dict]:
        img_t = TRANSFORM_FRUIT_RESNET(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            feat_resnet = self.fruit_backbone(img_t).cpu().numpy()

        img_arr = np.asarray(image.resize((128, 128)), dtype=np.float32) / 255.0
        gray = img_arr.mean(axis=2)
        feat_hog = hog(
            gray,
            orientations=12,
            pixels_per_cell=(6, 6),
            cells_per_block=(2, 2),
            feature_vector=True,
        ).reshape(1, -1)

        fused = np.hstack([
            self.sc_resnet.transform(feat_resnet),
            self.sc_hog.transform(feat_hog),
        ])
        proba = np.mean([
            elm.predict_proba_calibrated(fused, self.temperature)
            for elm in self.fruit_elms
        ], axis=0)[0]

        top_idx = np.argsort(proba)[::-1][:3]
        return [
            {
                "label": FRUIT_LABELS[int(idx)],
                "confidence": round(float(proba[int(idx)]), 4),
            }
            for idx in top_idx
        ]

    def _predict_imagenet(self, image: Image.Image) -> list[dict]:
        img_t = TRANSFORM_IMAGENET(image).unsqueeze(0)
        with torch.no_grad():
            out = self.imagenet_model(img_t)
            proba = torch.softmax(out, dim=1)[0]

        top10_idx = torch.topk(proba, 10).indices.tolist()

        seen, results = set(), []
        for idx in top10_idx:
            raw = self.imagenet_cats[idx]
            confidence = float(proba[idx])
            label = self._match(raw.lower()) or self._clean_label(raw)
            if label not in seen:
                seen.add(label)
                results.append({
                    "label": label,
                    "confidence": round(confidence, 4),
                    "raw_label": raw,
                })
            if len(results) >= 3:
                break

        return results

    def _match(self, raw_label: str) -> str | None:
        for friendly, keywords in self.keyword_map.items():
            if any(kw in raw_label for kw in keywords):
                return friendly
        return None

    def _clean_label(self, raw: str) -> str:
        return raw.split(",")[0].strip().lower().replace(" ", "_")


handler = ModelHandler()
