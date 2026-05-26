# KidVocab Vision

KidVocab Vision là web app học từ vựng tiếng Anh cho trẻ em thông qua camera. Người dùng đưa đồ vật hằng ngày vào khung quét, hệ thống nhận diện vật thể, hiển thị tên tiếng Anh, tên tiếng Việt, hình minh họa, phát âm mẫu và các hoạt động học tập như từ điển, quiz và luyện phát âm.

Dự án được xây dựng cho đồ án cuối kỳ môn Thị giác máy tính, tập trung vào trải nghiệm học tập trực quan và pipeline nhận diện ảnh trên web.

## Mục Tiêu

- Giúp trẻ học từ vựng tiếng Anh bằng các vật thật xung quanh.
- Nhận diện nhiều nhóm đối tượng thường gặp như đồ vật, động vật, đồ ăn, phương tiện, thiên nhiên và trái cây.
- Cung cấp giao diện học tập thân thiện: quét vật thể, xem từ điển, làm quiz, luyện phát âm.
- Bổ sung các bước tiền xử lý và đánh giá chất lượng ảnh để phần camera scan có tính học thuật hơn, không chỉ gọi model rồi trả kết quả.

## Chức Năng Chính

### 1. Quét Đồ Vật Bằng Camera

- Mở camera trực tiếp trên trình duyệt.
- Chụp frame hiện tại và gửi về backend để nhận diện.
- Hỗ trợ chọn ảnh từ thư viện nếu thiết bị không có camera.
- Hiển thị kết quả nhận diện gồm:
  - Tên tiếng Anh.
  - Tên tiếng Việt nếu có.
  - Phân loại chủ đề.
  - Độ tin cậy.
  - Top-3 dự đoán.
  - Cảnh báo nếu ảnh mờ, tối hoặc ít tương phản.

### 2. Học Từ Vựng Theo Đồ Vật

- Dữ liệu hiện có khoảng hơn 1000 đối tượng từ ImageNet.
- Các đối tượng được chia thành 6 nhóm chính:
  - Trái cây.
  - Động vật.
  - Đồ ăn.
  - Phương tiện.
  - Đồ vật.
  - Thiên nhiên.
- Mỗi từ có thể hiển thị tên tiếng Anh, tên tiếng Việt, hình ảnh minh họa, phát âm và thông tin ngắn.

### 3. Từ Điển Từ Vựng

- Xem toàn bộ danh sách từ vựng.
- Tìm kiếm theo tên tiếng Anh hoặc tiếng Việt.
- Lọc theo nhóm chủ đề.
- Card từ vựng có hiệu ứng lật để xem thông tin chi tiết.
- Hình minh họa được lấy từ Wikipedia/Wikimedia theo từ khóa, có fallback về emoji nếu không tìm được ảnh.

### 4. Quiz

- Sinh câu hỏi ngẫu nhiên từ dữ liệu từ vựng.
- Người học chọn đáp án đúng dựa trên hình ảnh/từ vựng.
- Có điểm số, tiến trình, hiệu ứng đúng/sai và tổng kết sau mỗi lượt chơi.

### 5. Luyện Phát Âm

- Phát âm mẫu bằng Web Speech API.
- Người dùng nói lại từ tiếng Anh.
- Trình duyệt nhận dạng giọng nói và chấm mức độ khớp cơ bản.
- Có phản hồi bằng sao và hiệu ứng khuyến khích.

## Điểm Thị Giác Máy Tính Trong Dự Án

Pipeline nhận diện hiện tại gồm các bước:

```text
Camera / Upload Image
        |
        v
Validate image
        |
        v
Image quality assessment
        |
        v
Preprocessing
        |
        v
Feature/model inference
        |
        v
Top-k prediction + learning UI
```

### Đánh Giá Chất Lượng Ảnh

Backend tính các chỉ số:

- `brightness`: độ sáng trung bình của ảnh.
- `contrast`: độ lệch chuẩn mức xám, dùng để ước lượng tương phản.
- `sharpness`: phương sai Laplacian, dùng để ước lượng độ nét/mờ.
- `issues`: danh sách vấn đề như `dark`, `too_bright`, `low_contrast`, `blurry`.

Nếu ảnh có chất lượng thấp, giao diện sẽ cảnh báo để người dùng quét lại gần hơn, đủ sáng hơn hoặc đổi góc chụp.

### Tiền Xử Lý Ảnh

Backend áp dụng:

- `exif_transpose`: sửa hướng ảnh theo metadata.
- `rgb_convert`: chuyển ảnh về RGB.
- `autocontrast`: cân bằng tương phản nhẹ.
- `sharpen`: làm nét nhẹ trước khi đưa vào model.

Các bước này giúp pipeline rõ ràng hơn về mặt xử lý ảnh đầu vào.

## Model Nhận Diện

Dự án hiện hỗ trợ 2 nhánh model:

### 1. ImageNet ResNet50

- Dùng `torchvision.models.resnet50` pretrained trên ImageNet.
- Nhận diện khoảng 1000 lớp đối tượng phổ biến.
- Đây là nhánh chính để app có thể học nhiều đồ vật hằng ngày, không bị giới hạn ở 5 loại trái cây.

### 2. Fruit Model ResNet18 + HOG + ELM

- Đây là nhánh model đã train riêng cho đề tài phân loại trái cây ban đầu.
- Dùng ResNet18 fine-tuned để trích đặc trưng ảnh.
- Trích thêm đặc trưng HOG ở kích thước 128x128.
- Chuẩn hóa hai nhóm đặc trưng bằng `sc_resnet.joblib` và `sc_hog.joblib`.
- Ghép đặc trưng ResNet + HOG rồi phân loại bằng ensemble 3 ELM model.
- Áp dụng temperature scaling từ `temperature.joblib`.
- Phân loại 5 loại trái cây:
  - Apple.
  - Banana.
  - Grape.
  - Orange.
  - Pomegranate.

Các artifact model cần có trong thư mục `model/`:

```text
model/resnet_finetuned.pth
model/elm_0_relu.joblib
model/elm_1_tanh.joblib
model/elm_2_sigmoid.joblib
model/sc_resnet.joblib
model/sc_hog.joblib
model/temperature.joblib
```

Nếu thiếu các file này, backend sẽ tắt nhánh fruit model. Người dùng vẫn có thể dùng nhánh ImageNet để nhận diện vật dụng hằng ngày.

## Công Nghệ Sử Dụng

- Backend: FastAPI.
- Frontend: HTML, CSS, JavaScript thuần.
- Computer Vision: PyTorch, TorchVision, PIL.
- Model: ResNet50 ImageNet, ResNet18 feature extractor, SVM.
- Speech: Web Speech API.
- Image source cho từ điển: Wikipedia/Wikimedia API.

## Cấu Trúc Thư Mục

```text
fruit_web_app/
├── main.py                    # FastAPI app, API routes, static serving
├── model_handler.py           # Load model, preprocessing, quality check, inference
├── generate_imagenet_dict.py  # Sinh dictionary từ ImageNet classes
├── update_vietnamese_names.py # Bổ sung tên tiếng Việt cho dictionary ImageNet
├── fix_specific_vn_names.py   # Sửa tay các nhãn ImageNet dịch máy chưa tốt
├── fruit_data.json            # Dữ liệu chi tiết cho 5 loại trái cây
├── imagenet_vn.json           # Dictionary mở rộng cho ImageNet objects
├── imagenet_full.json         # Dictionary ImageNet gốc/sinh tự động
├── requirements.txt           # Python dependencies
├── model/
│   ├── final_model.ipynb      # Notebook train fruit model
│   ├── resnet_finetuned.pth   # ResNet18 fine-tuned
│   ├── elm_*.joblib           # ELM ensemble
│   ├── sc_resnet.joblib       # Scaler đặc trưng ResNet
│   ├── sc_hog.joblib          # Scaler đặc trưng HOG
│   └── temperature.joblib     # Temperature scaling
└── static/
    ├── index.html             # Giao diện chính
    ├── app.js                 # Logic frontend
    └── style.css              # CSS giao diện
```

## Cài Đặt

Yêu cầu:

- Python 3.10 trở lên.
- Camera nếu muốn test scan trực tiếp.
- Kết nối internet nếu muốn tải ảnh minh họa từ Wikipedia/Wikimedia.

Cài dependencies:

```bash
pip install -r requirements.txt
```

## Chạy Ứng Dụng

Chạy server:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở trình duyệt:

```text
http://127.0.0.1:8000
```

Kiểm tra API health:

```text
http://127.0.0.1:8000/api/health
```

Ví dụ response:

```json
{
  "status": "ok",
  "fruit_ready": false,
  "imagenet_ready": true,
  "total_objects": 1055
}
```

Trong đó:

- `fruit_ready`: nhánh model trái cây đã sẵn sàng hay chưa.
- `imagenet_ready`: ResNet50 ImageNet đã sẵn sàng hay chưa.
- `total_objects`: tổng số từ vựng/đối tượng trong app.

## API Chính

### `GET /api/health`

Kiểm tra trạng thái hệ thống.

### `GET /api/all-objects`

Trả về toàn bộ dictionary từ vựng.

### `GET /api/object/{label}`

Lấy thông tin chi tiết của một object theo label.

### `POST /api/predict`

Nhận file ảnh và trả về kết quả nhận diện. Request dùng `multipart/form-data`:

- `file`: ảnh cần nhận diện.
- `mode`: nhánh model, gồm `fruit` hoặc `imagenet`.

Response gồm:

- `source`: nhánh model được dùng.
- `mode`: chế độ nhận diện được chọn.
- `results`: top prediction.
- `quality`: đánh giá chất lượng ảnh.
- `preprocessing`: các bước tiền xử lý đã áp dụng.
- `demo_mode`: có đang ở chế độ demo hay không.

Ví dụ:

```json
{
  "source": "imagenet",
  "results": [
    {
      "label": "backpack",
      "confidence": 0.82,
      "raw_label": "backpack"
    }
  ],
  "quality": {
    "brightness": 132.5,
    "contrast": 47.2,
    "sharpness": 310.8,
    "issues": [],
    "is_good": true
  },
  "preprocessing": [
    "exif_transpose",
    "rgb_convert",
    "autocontrast",
    "sharpen"
  ],
  "demo_mode": false
}
```

## Train Fruit Model Trên Kaggle

Notebook [model/final_model.ipynb](model/final_model.ipynb) dùng để train nhánh phân loại trái cây:

1. Load dataset 5 class.
2. Trích đặc trưng HOG từ ảnh resize 128x128.
3. Fine-tune ResNet18 trên 5 class trái cây.
4. Dùng ResNet18 fine-tuned làm backbone trích đặc trưng 512 chiều.
5. Chuẩn hóa đặc trưng ResNet và HOG.
6. Ghép đặc trưng rồi train ensemble 3 ELM model.
7. Tìm temperature tốt nhất và lưu toàn bộ artifact vào thư mục `model/`.

Các file runtime quan trọng là:

```text
model/resnet_finetuned.pth
model/elm_0_relu.joblib
model/elm_1_tanh.joblib
model/elm_2_sigmoid.joblib
model/sc_resnet.joblib
model/sc_hog.joblib
model/temperature.joblib
```

Trong app, người dùng có thể bấm nút chuyển giữa nhánh `Fruit model` và `ImageNet`.

## Hạn Chế Hiện Tại

- ResNet50 ImageNet là model pretrained nên có thể dự đoán sai với ảnh thực tế, góc chụp lạ hoặc vật thể nhỏ.
- Một số lớp ImageNet quá chuyên biệt, không thật sự phù hợp với trẻ em.
- `imagenet_vn.json` chưa được Việt hóa đầy đủ, nhiều `nameVn` vẫn là tiếng Anh.
- Ảnh minh họa lấy từ Wikipedia có thể sai với từ mơ hồ, ví dụ `apple` có thể cần ép thành `apple fruit`.
- Chưa có Grad-CAM để giải thích vùng ảnh mà model chú ý.
- Chưa có bộ test tự động đầy đủ cho API và frontend.
- Chưa có database lưu lịch sử học tập lâu dài.

## Hướng Phát Triển

- Thêm danh sách object phù hợp với trẻ em và ẩn các class quá lạ.
- Việt hóa toàn bộ từ vựng quan trọng trong `imagenet_vn.json`.
- Thêm Grad-CAM/heatmap để giải thích kết quả nhận diện.
- Thêm lịch sử nhận diện bằng `localStorage` hoặc database.
- Thêm thống kê học tập: số lần quét, từ đã học, điểm quiz trung bình.
- Thêm bộ ảnh mẫu để demo khi không có camera.
- Fine-tune model trên bộ dữ liệu đồ vật hằng ngày thay vì chỉ dùng pretrained ImageNet.
- Thêm evaluation report: confusion matrix, precision, recall, F1-score.

## Ý Nghĩa Đồ Án

Dự án kết hợp Computer Vision và giáo dục:

- Computer Vision dùng để nhận diện vật thể từ camera.
- Web app biến kết quả nhận diện thành hoạt động học tiếng Anh.
- Tiền xử lý ảnh và đánh giá chất lượng ảnh giúp pipeline có tính kỹ thuật hơn.
- Giao diện học tập giúp trẻ tương tác với vật thật, tăng khả năng ghi nhớ từ vựng.

## Tác Giả

Dự án đồ án cuối kỳ môn Thị giác máy tính.
