"""
SYNAPES SECURITY GATEWAY & MULTI-LAYER FIREWALL MIDDLEWARE
Hệ thống tường lửa ứng dụng đa tầng bảo vệ máy chủ:
1. Security Headers Middleware (OWASP Standard): Chống XSS, Clickjacking, MIME Sniffing, Frame Injection.
2. In-Memory IP Rate Limiter (Token Bucket): Giới hạn tần suất tải tệp & ngăn chặn tấn công DoS / Brute-force.
3. Server Fingerprint Cloaking: Ẩn thông tin công nghệ máy chủ (Uvicorn / Python version).
"""

import time
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Gắn các tiêu đề an ninh HTTP chuẩn OWASP trên toàn bộ phản hồi"""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # 1. Chống Clickjacking: Tuyệt đối không cho phép nhúng website vào iframe từ bên ngoài
        response.headers["X-Frame-Options"] = "DENY"

        # 2. Chống MIME-type sniffing: Buộc trình duyệt tuân thủ định dạng Content-Type đã khai báo
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. Kích hoạt bộ lọc XSS của trình duyệt
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 4. Bảo vệ thông tin liên kết chuyển tiếp
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 5. Khóa các quyền phần cứng thiết bị không cần thiết
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"

        # 6. Buộc kết nối mã hóa HTTPS (HSTS - 1 năm)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 7. Xóa hoặc ghi đè tiêu đề lộ dấu ấn máy chủ
        response.headers["Server"] = "SYNAPES-Shield-WAF/3.3"
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        # 8. Content Security Policy (CSP): Bảo vệ máy chủ chống Frame-Injection nhưng bảo đảm 100%
        # các CDN giao diện (Tailwind CDN, Google Fonts, KaTeX, Chart.js, jsPDF, html2canvas) tải thông suốt
        csp_directives = [
            "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:",
            "script-src * 'unsafe-inline' 'unsafe-eval' data: blob: https://cdn.tailwindcss.com",
            "style-src * 'unsafe-inline' https://fonts.googleapis.com",
            "font-src * data: https://fonts.gstatic.com",
            "img-src * data: blob: https:",
            "connect-src *",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response


class IPFirewallMiddleware(BaseHTTPMiddleware):
    """
    Tường lửa giới hạn tần suất truy cập theo địa chỉ IP (Rate Limiter & Anti-Flood):
    - Upload tệp: Giới hạn tối đa 8 lượt tải / 60 giây / IP (Chống vắt kiệt RAM & CPU).
    - API chung: Giới hạn tối đa 90 lượt gọi / 60 giây / IP.
    - Tự động thanh lọc bộ nhớ cache để chống rò rỉ RAM (Zero Memory Leak).
    """

    def __init__(self, app):
        super().__init__(app)
        # Lưu trữ: {ip: [(timestamp, path), ...]}
        self.request_history: Dict[str, List[Tuple[float, str]]] = {}
        self.last_cleanup = time.time()

        # Ngưỡng quy định
        self.UPLOAD_LIMIT = 8       # Max 8 tệp / phút
        self.API_LIMIT = 90         # Max 90 requests / phút
        self.WINDOW_SECONDS = 60    # Khung thời gian 60 giây

    def _get_client_ip(self, request: Request) -> str:
        """Trích xuất địa chỉ IP thực tế của client kể cả khi đi qua Cloudflare / Proxy"""
        # Ưu tiên tiêu đề xác thực từ Cloudflare
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip.strip()

        # X-Forwarded-For
        x_forwarded = request.headers.get("X-Forwarded-For")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()

        # Fallback IP máy khách trực tiếp
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def _cleanup_old_records(self, now: float):
        """Tự động dọn dẹp các bản ghi IP quá hạn để giải phóng RAM định kỳ"""
        if now - self.last_cleanup < 120:
            return
        self.last_cleanup = now
        expired_cutoff = now - (self.WINDOW_SECONDS * 2)

        stale_ips = []
        for ip, logs in self.request_history.items():
            valid_logs = [entry for entry in logs if entry[0] > expired_cutoff]
            if valid_logs:
                self.request_history[ip] = valid_logs
            else:
                stale_ips.append(ip)

        for ip in stale_ips:
            del self.request_history[ip]

    async def dispatch(self, request: Request, call_next) -> Response:
        now = time.time()
        client_ip = self._get_client_ip(request)
        path = request.url.path

        # Tự động thanh lọc cache định kỳ
        self._cleanup_old_records(now)

        # Bỏ qua kiểm tra đối với tài nguyên tĩnh hoặc trang chủ
        if path.startswith("/static") or path in ["/favicon.ico"]:
            return await call_next(request)

        # Lấy lịch sử truy cập của IP này
        ip_history = self.request_history.setdefault(client_ip, [])
        window_start = now - self.WINDOW_SECONDS
        
        # Chỉ giữ lại các request trong khung thời gian 60 giây
        recent_requests = [entry for entry in ip_history if entry[0] > window_start]
        self.request_history[client_ip] = recent_requests

        # Kiểm tra ngưỡng tải tệp (Upload Rate Limit)
        if "/scan/upload" in path or "/scan/async" in path:
            upload_count = sum(1 for entry in recent_requests if "/scan/upload" in entry[1] or "/scan/async" in entry[1])
            if upload_count >= self.UPLOAD_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Tường lửa an ninh: Tần suất tải tệp vượt quá ngưỡng an toàn ({self.UPLOAD_LIMIT} tệp/phút). Vui lòng đợi 60 giây trước khi thử lại.",
                        "error_code": "RATE_LIMIT_EXCEEDED"
                    },
                    headers={"Retry-After": "60"}
                )

        # Kiểm tra ngưỡng gọi API chung (Ngoại trừ endpoint polling trạng thái tiến trình ngầm)
        if path.startswith("/api/") and "/scan/status/" not in path:
            if len(recent_requests) >= self.API_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Tường lửa an ninh: Tần suất truy vấn API vượt quá giới hạn cho phép. Vui lòng giảm tốc độ truy cập.",
                        "error_code": "RATE_LIMIT_EXCEEDED"
                    },
                    headers={"Retry-After": "60"}
                )

        # Ghi nhận request hợp lệ
        self.request_history[client_ip].append((now, path))

        return await call_next(request)

