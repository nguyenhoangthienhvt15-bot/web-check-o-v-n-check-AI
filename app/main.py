import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import scan

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Hệ thống phân tích và phát hiện Đạo văn & Văn bản AI (Binoculars + MinHash LSH)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix=f"{settings.API_V1_STR}", tags=["Scan"])

@app.get("/", response_class=HTMLResponse)
def serve_home_ui():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Hệ thống Kiểm định Đạo văn & Văn bản AI đang hoạt động.</h1>"

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
