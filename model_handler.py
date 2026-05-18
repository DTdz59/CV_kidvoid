import io, json
import numpy as np
import joblib
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image, ImageFilter, ImageOps

FRUIT_LABELS = ['apple', 'banana', 'grape', 'orange', 'pomegranate']
FRUIT_CONFIDENCE_THRESHOLD = 0.65

TRANSFORM_RESNET18 = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

TRANSFORM_IMAGENET = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


class ModelHandler:
    def __init__(self):
        self.fruit_extractor  = None
        self.fruit_svm        = None
        self.imagenet_model   = None
        self.imagenet_cats    = None   # list of 1000 category strings
        self.vn_dict          = {}     # imagenet_vn.json
        self.keyword_map      = {}     # friendly_name → [keywords]
        self.fruit_ready      = False
        self.imagenet_ready   = False

    def load(self, svm_path="model/svm_resnet.pkl",
             vn_dict_path="imagenet_vn.json"):

        # ── Fruit model ──────────────────────────────────────
        try:
            resnet18 = models.resnet18(
                weights=models.ResNet18_Weights.IMAGENET1K_V1)
            self.fruit_extractor = torch.nn.Sequential(
                *list(resnet18.children())[:-1])
            self.fruit_extractor.eval()
            self.fruit_svm   = joblib.load(svm_path)
            self.fruit_ready = True
            print("✅ Fruit model loaded")
        except FileNotFoundError:
            print("⚠️  model/svm_resnet.pkl not found — fruit model disabled")
        except Exception as e:
            print(f"⚠️  Fruit model error: {e}")

        # ── ImageNet model ────────────────────────────────────
        weights = models.ResNet50_Weights.IMAGENET1K_V1
        resnet50 = models.resnet50(weights=weights)
        resnet50.eval()
        self.imagenet_model = resnet50
        self.imagenet_cats  = weights.meta["categories"]
        self.imagenet_ready = True
        print("✅ ImageNet model loaded (1000 classes)")

        # ── VN dictionary + keyword map ───────────────────────
        with open(vn_dict_path, encoding="utf-8") as f:
            self.vn_dict = json.load(f)
        self.keyword_map = {
            k: [kw.lower() for kw in v["keywords"]]
            for k, v in self.vn_dict.items()
        }
        print(f"✅ VN dictionary: {len(self.vn_dict)} objects")

    # ── Public predict ────────────────────────────────────────
    def predict(self, image_bytes: bytes) -> dict:
        raw_image = ImageOps.exif_transpose(
            Image.open(io.BytesIO(image_bytes))
        ).convert("RGB")
        quality = self._quality_report(raw_image)
        image = self._preprocess_image(raw_image)

        # 1. Try fruit model first
        if self.fruit_ready:
            fruit_result = self._predict_fruit(image)
            if fruit_result["confidence"] >= FRUIT_CONFIDENCE_THRESHOLD:
                return {
                    "source": "fruit",
                    "results": [fruit_result],
                    "quality": quality,
                    "preprocessing": ["exif_transpose", "rgb_convert", "autocontrast", "sharpen"],
                }

        # 2. Fall back to ImageNet
        results = self._predict_imagenet(image)
        return {
            "source": "imagenet",
            "results": results,
            "quality": quality,
            "preprocessing": ["exif_transpose", "rgb_convert", "autocontrast", "sharpen"],
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

    # ── Fruit inference ───────────────────────────────────────
    def _predict_fruit(self, image: Image.Image) -> dict:
        img_t = TRANSFORM_RESNET18(image).unsqueeze(0)
        with torch.no_grad():
            feat = self.fruit_extractor(img_t)
        features = feat.numpy().flatten().reshape(1, -1)
        proba    = self.fruit_svm.predict_proba(features)[0]
        top_idx  = int(np.argmax(proba))
        return {
            "label":      FRUIT_LABELS[top_idx],
            "confidence": round(float(proba[top_idx]), 4),
        }

    # ── ImageNet inference ────────────────────────────────────
    def _predict_imagenet(self, image: Image.Image) -> list[dict]:
        img_t = TRANSFORM_IMAGENET(image).unsqueeze(0)
        with torch.no_grad():
            out   = self.imagenet_model(img_t)
            proba = torch.softmax(out, dim=1)[0]

        top10_idx = torch.topk(proba, 10).indices.tolist()

        seen, results = set(), []
        for idx in top10_idx:
            raw       = self.imagenet_cats[idx]
            confidence = float(proba[idx])
            # Try keyword match first, else use cleaned raw label
            label = self._match(raw.lower()) or self._clean_label(raw)
            if label not in seen:
                seen.add(label)
                results.append({
                    "label":      label,
                    "confidence": round(confidence, 4),
                    "raw_label":  raw,
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
        """Convert raw ImageNet label to a clean key."""
        return raw.split(",")[0].strip().lower().replace(" ", "_")


handler = ModelHandler()
