import os
import re
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.security_middleware import SecurityHeadersMiddleware, IPFirewallMiddleware
from app.api.v1.endpoints import scan

# Kiểm soát chế độ hiển thị tài liệu API (Anti-Reconnaissance):
# Mặc định ẩn 100% Swagger UI (/docs) và OpenAPI Schema (/openapi.json) trên môi trường công khai
enable_swagger = os.getenv("ENABLE_SWAGGER", "false").lower() == "true"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if enable_swagger else None,
    docs_url="/docs" if enable_swagger else None,
    redoc_url="/redoc" if enable_swagger else None,
    description="Hệ thống phân tích và phát hiện Đạo văn & Văn bản AI (Binoculars + MinHash LSH)",
)

# 1. Kích hoạt Tường lửa An ninh Đa tầng (Multi-Layer Security Gateway)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(IPFirewallMiddleware)

# 2. Cấu hình kiểm soát nguồn gốc chia sẻ tài nguyên (CORS Hardening)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Phục vụ tài nguyên tĩnh (Static Files: logo, images)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(scan.router, prefix=f"{settings.API_V1_STR}", tags=["Scan"])

def _get_clean_html(template_filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "templates", template_filename)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # Loại bỏ hoàn toàn HTML comments để chống lộ cấu trúc giải thuật và ghi chú nội bộ
    html = re.sub(r'<!--(?!\s*\[if).*?-->', '', html, flags=re.DOTALL)
    # Loại bỏ các dòng trống dư thừa
    html = re.sub(r'\n\s*\n', '\n', html)
    return html

@app.get("/", response_class=HTMLResponse)
@app.head("/")
def serve_home_ui():
    html = _get_clean_html("index.html")
    if html:
        return html
    return "<h1>Hệ thống Kiểm định Đạo văn & Văn bản AI đang hoạt động.</h1>"

@app.get("/verify", response_class=HTMLResponse)
@app.head("/verify")
def serve_verify_ui():
    html = _get_clean_html("verify.html")
    if html:
        return html
    return "<h1>Cổng Xác thực Biên bản SYNAPES AUDIT</h1>"

@app.on_event("startup")
def run_startup_self_test():
    """Tự động kiểm thử hệ thống giám định (Self-Healing Regression Gate) chạy trên luồng ngầm không gây nghẽn cổng kết nối"""
    def _run_in_background():
        try:
            from app.engines.regression_harness import ForensicRegressionHarness
            harness = ForensicRegressionHarness()
            report = harness.run_all_benchmarks()
            print(f"[SYNAPES AUDIT] Self-Verifying Regression Gate: {report['passed_tests']}/{report['total_tests']} tests passed.")
            for d in report.get("details", []):
                status_flag = "[PASS]" if d["status"] == "PASSED" else "[FAIL]"
                print(f" {status_flag} {d['name']}: {d['status']} {d['error'] or ''}")
        except Exception as e:
            print(f"[SYNAPES AUDIT] Startup regression check error: {e}")

    threading.Thread(target=_run_in_background, daemon=True).start()

@app.get("/health")
@app.get("/healthz")
@app.head("/health")
@app.head("/healthz")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "engine_version": "v3.3-self-verifying-multi-factor"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
