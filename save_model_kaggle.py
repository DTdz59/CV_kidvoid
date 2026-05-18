# Chạy file này trên Kaggle (thêm vào notebook) để lưu model
# Sau đó download file svm_resnet.pkl và đặt vào thư mục model/

import os
import cv2
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import joblib
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

DATASET_PATH = "/kaggle/input/datasets/lnguynphchng/data-fruit-5class/data_PJ"
IMG_SIZE = 128

# ── 1. Load ảnh ──────────────────────────────────────────────────────────────
images, labels = [], []
label_names = sorted(os.listdir(DATASET_PATH))   # sort để thứ tự nhất quán
print("Classes:", label_names)

for label, folder in enumerate(label_names):
    for file in os.listdir(os.path.join(DATASET_PATH, folder)):
        path = os.path.join(DATASET_PATH, folder, file)
        img = cv2.imread(path)
        if img is None:
            continue
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) / 255.0
        images.append(img)
        labels.append(label)

images = np.array(images)
labels = np.array(labels)
print(f"Total: {len(images)} ảnh")

# ── 2. Trích đặc trưng ResNet18 ──────────────────────────────────────────────
resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
extractor.eval()

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

features = []
for img in images:
    img_t = transform((img * 255).astype("uint8")).unsqueeze(0)
    with torch.no_grad():
        feat = extractor(img_t)
    features.append(feat.numpy().flatten())

features = np.array(features)
print("Feature shape:", features.shape)

# ── 3. Train SVM (probability=True để lấy confidence) ───────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

svm = SVC(kernel="rbf", probability=True, random_state=42)
svm.fit(X_train, y_train)

acc = accuracy_score(y_test, svm.predict(X_test))
print(f"Accuracy: {acc:.4f} ({acc*100:.2f}%)")

# ── 4. Lưu model ─────────────────────────────────────────────────────────────
joblib.dump(svm, "/kaggle/working/svm_resnet.pkl")
print("Saved: svm_resnet.pkl")
print("→ Download file này rồi đặt vào thư mục fruit_web_app/model/")
