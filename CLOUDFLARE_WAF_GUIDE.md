# HƯỚNG DẪN THIẾT LẬP TƯỜNG LỬA ĐÁM MÂY (CLOUDFLARE WAF) CHO SYNAPES AUDIT

Tài liệu hướng dẫn cấu hình **Cloudflare (Gói miễn phí 100%)** làm tường lửa biên (Edge WAF) đứng trước máy chủ Render, bảo vệ hoàn toàn hệ thống khỏi tấn công DDoS, quét dò điểm yếu, rò rỉ IP máy chủ gốc, và công cụ botnet tự động.

---

## 1. Cơ chế hoạt động của Tường lửa Cloudflare WAF

```
[ Người dùng / Hacker ]
           │
           ▼
[ Cloudflare Edge Network ]  <-- Bật đám mây màu cam (Proxied)
  - Ẩn hoàn toàn địa chỉ IP gốc của Render
  - Tự động lọc sạch tấn công DDoS Layer 3/4 và Layer 7
  - Chặn các bot dò quét (Burp Suite, Nikto, sqlmap, Python requests)
  - Xác thực người dùng bằng Cloudflare Turnstile (CAPTCHA vô hình)
           │
           ▼ (Chỉ lưu lượng sạch được chuyển tiếp)
[ Máy chủ Render (synapeseducheck.onrender.com) ]
  - Tiếp nhận request an toàn với IP gốc được chuyển qua header CF-Connecting-IP
```

---

## 2. Các bước thiết lập từng bước (Step-by-Step)

### Bước 1: Trỏ tên miền qua Cloudflare
1. Đăng ký tài khoản miễn phí tại [cloudflare.com](https://dash.cloudflare.com/).
2. Thêm tên miền của bạn (ví dụ: `synapes.edu.vn` hoặc `synapesaudit.vn`).
3. Đổi Nameserver của nhà đăng ký tên miền (PA Vietnam, Mat Bao, GoDaddy, Namecheap...) về 2 địa chỉ Nameserver của Cloudflare.

### Bước 2: Thiết lập bản ghi DNS Proxy (Đám mây màu cam)
1. Trong bảng điều khiển Cloudflare $\rightarrow$ Chọn mục **DNS** $\rightarrow$ **Records**.
2. Thêm bản ghi **CNAME**:
   - **Type:** `CNAME`
   - **Name:** `@` (hoặc tiền tố subdomain như `check` hay `audit`)
   - **Target:** `synapeseducheck.onrender.com`
   - **Proxy status:** Bắt buộc bật **Proxied (Đám mây màu cam ☁️)**.
3. Trong Render Dashboard $\rightarrow$ **Settings** $\rightarrow$ **Custom Domains** $\rightarrow$ Thêm tên miền tùy chỉnh của bạn để Render tự động cấp chứng chỉ SSL.

### Bước 3: Kích hoạt chế độ Chống Bot tự động (Bot Fight Mode)
1. Trong Cloudflare $\rightarrow$ Mục **Security** $\rightarrow$ **Bots**.
2. Bật công tắc **Bot Fight Mode**:
   - Tự động nhận diện và chặn các công cụ quét tự động của hacker (như Burp Suite, Python Scrapy, curl flood, headless browser độc hại).

### Bước 4: Thiết lập Quy tắc Tường lửa ứng dụng (WAF Custom Rules)
Vào mục **Security** $\rightarrow$ **WAF** $\rightarrow$ **Custom rules** $\rightarrow$ Chọn **Create rule**:

1. **Quy tắc 1: Khóa công cụ tự động tấn công API upload**
   - **Field:** `URI Path` contains `/scan/upload`
   - **AND Threat Score:** `greater than 15`
   - **Action:** `Managed Challenge` (Bắt xác thực CAPTCHA nếu phát hiện hành vi nghi vấn).

2. **Quy tắc 2: Chặn truy cập từ các quốc gia rủi ro (Ngoại trừ khu vực hoạt động)**
   - Nếu hệ thống chỉ phục vụ tại Việt Nam hoặc Đông Nam Á:
   - **Field:** `Country` is not in `Vietnam`
   - **AND URI Path:** contains `/scan/upload`
   - **Action:** `Managed Challenge`.

### Bước 5: Bật chế độ "Under Attack Mode" khi bị tấn công dồn dập
- Nếu phát hiện lưu lượng truy cập tăng vọt bất thường hoặc bị tấn công DDoS:
- Trong Cloudflare Dashboard $\rightarrow$ Mục **Overview** $\rightarrow$ Bật công tắc **Under Attack Mode**.
- Toàn bộ người truy cập sẽ đi qua màn hình kiểm tra 5 giây của Cloudflare trước khi vào web, bảo vệ máy chủ Render không bị sập.

---

## 3. Danh sách các tầng bảo vệ hiện có trên hệ thống

| Tầng bảo vệ | Thành phần phụ trách | Chức năng an ninh |
| :--- | :--- | :--- |
| **Lớp 1: Biên mạng** | Cloudflare WAF (DNS Proxy) | Ẩn IP máy chủ gốc, lọc sạch tấn công DDoS, chặn botnet. |
| **Lớp 2: Ứng dụng** | `SecurityHeadersMiddleware` | Gắn bộ tiêu đề OWASP: CSP, X-Frame-Options (DENY), HSTS, nosniff, ẩn Server header. |
| **Lớp 3: Tần suất** | `IPFirewallMiddleware` | Giới hạn 8 tệp/phút/IP và 90 API calls/phút/IP. Trả mã 429 khi vượt ngưỡng. |
| **Lớp 4: Tệp Upload** | `validate_and_sanitize_upload` | Kiểm tra Magic Bytes nhị phân, chống Zip Bomb (max 35MB giải nén), chống mã nhị phân ngụy trang. |
| **Lớp 5: Dữ liệu XML** | `convert_omml_in_xml` | Khử độc XML, chống tấn công XXE (XML External Entity) và Billion Laughs. |
| **Lớp 6: Giao diện** | `initSecurityShield` (JS) | Khóa chuột phải, vô hiệu hóa phím tắt DevTools (F12, Ctrl+U, Ctrl+Shift+I). |
| **Lớp 7: Hạ tầng** | Docker Non-Root User | Chạy tiến trình dưới quyền `appuser` (UID 10001), cô lập hoàn toàn quyền quản trị máy chủ. |
