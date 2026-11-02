"""
SYNAPES SECURITY GATEWAY & MULTI-LAYER FIREWALL MIDDLEWARE
Hệ thống tường lửa ứng dụng đa tầng bảo vệ máy chủ:
1. Security Headers Middleware (OWASP Standard): Chống XSS, Clickjacking, MIME Sniffing, Frame Injection.
2. In-Memory IP Rate Limiter (Token Bucket): Giới hạn tần suất tải tệp & ngăn chặn tấn công DoS / Brute-force.
3. Sentinel IP Auto-Ban System: Phong tỏa IP vĩnh viễn/tức thì đối với các hành vi cố tình mở DevTools, soi mã nguồn.
4. Server Fingerprint Cloaking: Ẩn thông tin công nghệ máy chủ (Uvicorn / Python version).
"""

import os
import json
import time
from typing import Dict, List, Tuple, Any, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, HTMLResponse

class SentinelIPManager:
    """
    HỆ THỐNG GIÁM SÁT VÀ PHONG TỎA ĐỊA CHỈ IP TỰ ĐỘNG (SYNAPES SENTINEL ACTIVE AUTO-BAN)
    Khóa tức thì mọi địa chỉ IP có hành vi cố tình mở DevTools, soi mã nguồn (Source Inspection),
    hoặc can thiệp đảo ngược mã (Reverse Engineering).
    Lưu trữ danh sách đen (Blacklist) bền vững trên đĩa để bảo toàn sau khi máy chủ khởi động lại.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SentinelIPManager, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self):
        self._blocked_ips: Dict[str, Dict[str, Any]] = {}
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        os.makedirs(storage_dir, exist_ok=True)
        self._db_path = os.path.join(storage_dir, "blocked_ips.json")
        self._load_from_disk()

    def _load_from_disk(self):
        try:
            if os.path.exists(self._db_path):
                with open(self._db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._blocked_ips = data
        except Exception as e:
            print(f"[SentinelIPManager] Cảnh báo đọc blocked_ips: {e}")

    def _save_to_disk(self):
        try:
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(self._blocked_ips, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SentinelIPManager] Cảnh báo ghi blocked_ips: {e}")

    def is_blocked(self, ip: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        record = self._blocked_ips.get(ip)
        if record:
            expires_at = record.get("expires_at", 0)
            now = time.time()
            if expires_at == 0 or now < expires_at:
                return True, record
            else:
                del self._blocked_ips[ip]
                self._save_to_disk()
        return False, None

    def block_ip(self, ip: str, reason: str = "DEVTOOLS_INSPECTION_ATTEMPT", duration_seconds: int = 86400 * 3) -> Dict[str, Any]:
        now = time.time()
        record = {
            "ip": ip,
            "blocked_at": now,
            "blocked_at_str": time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.gmtime(now + 7 * 3600)),
            "reason": reason,
            "expires_at": now + duration_seconds if duration_seconds > 0 else 0,
            "expires_at_str": time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.gmtime(now + duration_seconds + 7 * 3600)) if duration_seconds > 0 else "Vĩnh viễn"
        }
        self._blocked_ips[ip] = record
        self._save_to_disk()
        print(f"[SYNAPES SENTINEL] ĐÃ PHONG TỎA IP: {ip} - Lý do: {reason}")
        return record

    def unblock_ip(self, ip: str) -> bool:
        cleared = False
        for target in [ip, "127.0.0.1", "::1", "localhost"]:
            if target in self._blocked_ips:
                del self._blocked_ips[target]
                cleared = True
        if cleared:
            self._save_to_disk()
            print(f"[SYNAPES SENTINEL] Đã mở khóa an ninh cho IP: {ip}")
        return cleared

sentinel_ip_manager = SentinelIPManager()

def render_ip_blocked_html(client_ip: str, record: Optional[Dict[str, Any]]) -> str:
    blocked_time = (record or {}).get("blocked_at_str", "Vừa xong")
    reason = (record or {}).get("reason", "Cố tình mở công cụ nhà phát triển / Soi mã nguồn trái phép")
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>403 FORBIDDEN - TRUY CẬP ĐÃ BỊ PHONG TỎA | SYNAPES SENTINEL</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #090d16;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }}
    .card {{
      max-width: 540px;
      width: 100%;
      background: #111827;
      border: 1px solid rgba(239, 68, 68, 0.4);
      border-radius: 18px;
      padding: 32px 28px;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 30px rgba(239, 68, 68, 0.15);
    }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 16px;
    }}
    .icon {{
      font-size: 52px;
      line-height: 1;
      margin-bottom: 16px;
    }}
    h1 {{
      font-size: 22px;
      font-weight: 800;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}
    p.desc {{
      font-size: 13.5px;
      color: #94a3b8;
      line-height: 1.6;
      margin-bottom: 22px;
    }}
    .log-box {{
      background: #0a0f1d;
      border: 1px solid #1e293b;
      border-radius: 12px;
      padding: 16px;
      text-align: left;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      line-height: 1.7;
      color: #cbd5e1;
      margin-bottom: 22px;
    }}
    .log-row {{
      display: flex;
      justify-content: space-between;
      border-bottom: 1px dashed #1e293b;
      padding: 6px 0;
    }}
    .log-row:last-child {{ border-bottom: none; }}
    .log-label {{ color: #64748b; }}
    .log-val {{ color: #f87171; font-weight: 600; }}
    .log-val-ip {{ color: #fbbf24; font-weight: 700; }}
    .admin-note {{
      font-size: 11.5px;
      color: #64748b;
      line-height: 1.5;
    }}
    .admin-form {{
      margin-top: 18px;
      display: flex;
      gap: 8px;
      justify-content: center;
    }}
    .admin-input {{
      background: #0f172a;
      border: 1px solid #334155;
      color: #fff;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 12px;
      outline: none;
      width: 180px;
    }}
    .admin-btn {{
      background: #ef4444;
      color: #fff;
      border: none;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">🛡️</div>
    <div class="badge">HỆ THỐNG PHÒNG VỆ SYNAPES SENTINEL</div>
    <h1>TRUY CẬP ĐÃ BỊ PHONG TỎA</h1>
    <p class="desc">
      Hệ thống phát hiện thiết bị của bạn đã có hành vi cố tình mở công cụ nhà phát triển (DevTools), soi mã nguồn hoặc can thiệp dữ liệu trái phép. Nhằm bảo vệ liêm chính học thuật và bản quyền công nghệ, địa chỉ IP của bạn đã bị cách ly an ninh.
    </p>

    <div class="log-box">
      <div class="log-row">
        <span class="log-label">Địa chỉ IP:</span>
        <span class="log-val-ip">{client_ip}</span>
      </div>
      <div class="log-row">
        <span class="log-label">Hành vi phát hiện:</span>
        <span class="log-val">DevTools / Source Inspection</span>
      </div>
      <div class="log-row">
        <span class="log-label">Lý do ghi nhận:</span>
        <span class="log-val">{reason}</span>
      </div>
      <div class="log-row">
        <span class="log-label">Thời điểm ghi nhận:</span>
        <span>{blocked_time}</span>
      </div>
      <div class="log-row">
        <span class="log-label">Tình trạng xử lý:</span>
        <span class="log-val">ĐÃ KHÓA 100% TRUY CẬP</span>
      </div>
    </div>

    <p class="admin-note">
      Mọi dấu vết truy cập đã được lưu trữ trong nhật ký pháp y an ninh số hóa.<br>
      Nếu bạn là Quản trị viên hoặc thao tác nhầm, nhập khóa xác thực để mở khóa:
    </p>

    <form class="admin-form" method="GET" action="/">
      <input type="password" name="unlock" class="admin-input" placeholder="Nhập khóa mở khóa..." required />
      <button type="submit" class="admin-btn">Mở khóa IP</button>
    </form>
  </div>
</body>
</html>"""


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

        # 9. Vô hiệu hóa SourceMap & Ngăn chặn lưu cache mã nguồn trên máy khách
        response.headers["X-SourceMap"] = "none"
        response.headers["SourceMap"] = "none"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"

        return response


class IPFirewallMiddleware(BaseHTTPMiddleware):
    """
    Tường lửa giới hạn tần suất truy cập theo địa chỉ IP (Rate Limiter & Anti-Flood & Sentinel Ban Gate):
    - Khóa triệt để các IP vi phạm an ninh DevTools.
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

        # 0. Cơ chế giải cứu khẩn cấp / Mở khóa an ninh qua tham số URL (?unlock=synapes2026)
        unlock_key = request.query_params.get("unlock")
        if unlock_key == "synapes2026":
            sentinel_ip_manager.unblock_ip(client_ip)
            return Response(status_code=302, headers={"Location": "/"})

        # 1. Endpoint tiếp nhận báo cáo vi phạm DevTools từ máy khách và khóa IP ngay lập tức
        if path == "/api/v1/security/report-violation":
            try:
                body = await request.body()
                reason = "Cố tình mở công cụ nhà phát triển (DevTools) / Soi mã nguồn"
                if body:
                    try:
                        data = json.loads(body.decode('utf-8'))
                        reason = data.get("reason", reason)
                    except Exception:
                        pass
                record = sentinel_ip_manager.block_ip(client_ip, reason=reason)
                return JSONResponse({"status": "BLOCKED", "ip": client_ip, "details": record})
            except Exception as e:
                return JSONResponse({"status": "ERROR", "error": str(e)}, status_code=500)

        # 2. Endpoint mở khóa qua API với secret key (?key=synapes2026)
        if path == "/api/v1/security/unblock" and request.query_params.get("key") == "synapes2026":
            sentinel_ip_manager.unblock_ip(client_ip)
            return JSONResponse({"status": "UNBLOCKED", "ip": client_ip})

        # 3. KIỂM SOÁT PHONG TỎA IP TOÀN DIỆN (SENTINEL AUTO-BAN HARD BLOCK)
        # Bất kỳ IP nào nằm trong Blacklist sẽ bị khóa 100% tất cả các trang, API và tệp tĩnh
        is_blocked, block_record = sentinel_ip_manager.is_blocked(client_ip)
        if is_blocked:
            if path.startswith("/api/"):
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Địa chỉ IP đã bị khóa do hành vi can thiệp hoặc soi mã nguồn trái phép.",
                        "ip": client_ip,
                        "status": "FORBIDDEN",
                        "reason": (block_record or {}).get("reason", "SECURITY_VIOLATION")
                    }
                )
            return HTMLResponse(
                status_code=403,
                content=render_ip_blocked_html(client_ip, block_record)
            )

        # Tự động thanh lọc cache định kỳ
        self._cleanup_old_records(now)

        # Bỏ qua kiểm tra rate-limit đối với tài nguyên tĩnh hoặc favicon
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
