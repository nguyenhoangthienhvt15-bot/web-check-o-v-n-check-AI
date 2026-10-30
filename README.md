# 🔍 Academic AI Detection & Plagiarism Checker Engine

Hệ thống dịch vụ Web & API phân tích tính toàn vẹn học thuật toàn diện:
- **AI Detection:** Sử dụng cơ chế Zero-shot Binoculars (ICML 2024) dựa trên tỷ lệ Perplexity và Cross-Perplexity giữa cặp mô hình ngôn ngữ lớn (Observer vs Performer).
- **Plagiarism Detection:** Băm $k$-shingling n-gram và MinHash Locality-Sensitive Hashing (LSH) cho phép tra cứu $O(1)$ trên tập kho văn bản lớn.
- **Hạ tầng bất đồng bộ:** FastAPI Gateway + Celery Task Queue + Redis Broker + Docker Compose.

---

## 📂 Cấu trúc thư mục

```plaintext
academic-checker-system/
├── app/
│   ├── api/v1/endpoints/
│   │   └── scan.py             # API tiếp nhận văn bản & polling kết quả
│   ├── core/
│   │   ├── config.py           # Cấu hình Pydantic & tham số
│   │   └── celery_app.py       # Khởi tạo Celery app kết nối Redis
│   ├── engines/
│   │   ├── ai_detector.py      # Binoculars Engine (PyTorch / Transformers)
│   │   └── plagiarism.py       # MinHash LSH Engine (datasketch)
│   ├── workers/
│   │   └── tasks.py            # Celery background tasks
│   └── main.py                 # FastAPI Application entrypoint
├── frontend-components/
│   └── Footer.tsx              # Component React/Next.js Footer chuẩn UI
├── nginx/
│   └── academic_checker.conf   # Cấu hình Nginx Reverse Proxy
├── .github/workflows/
│   └── deploy.yml              # CI/CD: Linting, Docker build GHCR & Auto deploy VPS
├── docker-compose.yml          # Môi trường chạy Local
├── docker-compose.prod.yml     # Môi trường chạy Production trên VPS
├── Dockerfile                  # Docker Image đóng gói FastAPI & Worker
├── pyproject.toml / .flake8    # Cấu hình Black & Flake8 PEP 8
└── requirements.txt            # Danh sách thư viện Python
```

---

## 🚀 Khởi chạy cục bộ (Local Development)

### 1. Khởi chạy bằng Docker Compose
```bash
docker compose up --build
```
API Gateway sẽ sẵn sàng tại: `http://localhost:8000`  
Tài liệu Swagger UI tương tác: `http://localhost:8000/docs`

### 2. Kiểm tra API bằng Curl
**Gửi văn bản quét:**
```bash
curl -X POST "http://localhost:8000/api/v1/scan" \
     -H "Content-Type: application/json" \
     -d '{"content": "Machine learning and artificial intelligence are transforming modern research methodologies across diverse academic fields."}'
```
*Phản hồi:*
```json
{"task_id": "964bc3e4-c5a4-44df-bfa5-715764d0473a", "status": "QUEUED"}
```

**Truy vấn kết quả:**
```bash
curl -X GET "http://localhost:8000/api/v1/scan/964bc3e4-c5a4-44df-bfa5-715764d0473a"
```

---

## 👨‍💻 Tác giả & Bản quyền
- **Phát triển bởi:** KS Nguyễn Hoàng Thiện [SYNAPES EDU]
- **Email liên hệ:** [nguyenhoangthien.hvt.15@gmail.com](mailto:nguyenhoangthien.hvt.15@gmail.com)

