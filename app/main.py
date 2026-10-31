import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.endpoints import scan

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Hệ thống phân tích và phát hiện Đạo văn & Văn bản AI (Binoculars + MinHash LSH)",
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

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

@app.on_event("startup")
def run_startup_self_test():
    """Tự động kiểm thử hệ thống giám định (Self-Healing Regression Gate) khi khởi động"""
    try:
        from app.engines.regression_harness import ForensicRegressionHarness
        harness = ForensicRegressionHarness()
        report = harness.run_all_benchmarks()
        print(f"[SYNAPES AUDIT] Self-Verifying Regression Gate: {report['passed_tests']}/{report['total_tests']} tests passed.")
        for d in report["details"]:
            status_flag = "✓" if d["status"] == "PASSED" else "✗"
            print(f" {status_flag} {d['name']}: {d['status']} {d['error'] or ''}")
    except Exception as e:
        print(f"[SYNAPES AUDIT] Startup regression check error: {e}")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "engine_version": "v3.3-self-verifying-multi-factor"
    }
