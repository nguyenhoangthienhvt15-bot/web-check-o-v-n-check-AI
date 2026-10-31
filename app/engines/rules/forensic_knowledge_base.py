"""
FORENSIC KNOWLEDGE BASE & CLEAN DATA REGISTRY
Hệ thống lưu trữ và bảo tồn quy tắc giám định pháp y học thuật chuẩn (Golden Ruleset).
Đảm bảo tính bất biến của các tập dữ liệu sạch, ngăn chặn triệt để tình trạng hồi quy (regression)
qua mỗi phiên bản cập nhật.
"""

from typing import List, Tuple, Dict, Any

# 1. DANH MỤC DẤU ẤN CON NGƯỜI (HUMAN FINGERPRINTS)
# Các lỗi gõ phím, thói quen Telex, văn phong khẩu ngữ tự sự chứng minh tác giả con người tự soạn thảo
HUMAN_TYPO_PATTERNS: List[Tuple[str, str]] = [
    (r"\bsever\b", "Lỗi gõ phím từ mượn 'sever' (thiếu chữ 'r' -> 'server')"),
    (r"\bchi sẻ\b", "Lỗi gõ phím 'chi sẻ' (gõ thiếu âm 'a' -> 'chia sẻ')"),
    (r"\btrướcc\b", "Lỗi gõ phím Telex dư ký tự 'trướcc'"),
    (r"\bđầu dọc\b", "Lỗi gõ nhầm âm vị 'đầu dọc' (thực chất là 'đầu độc bảng định tuyến')"),
    (r"\bphiên bản đăng nhập\b", "Diễn đạt nhầm 'phiên bản đăng nhập' (đúng là 'phiên đăng nhập')"),
    (r"\b(wifi|wi-fi)\s+công cộng\b", "Chủ đề trải nghiệm mạng công cộng đời thường"),
    (r"^(một ngày đẹp trời|khi bạn|hãy tưởng tượng|thử nghĩ xem|nói một cách đơn giản)", "Văn phong khẩu ngữ, tự sự đời thường mang tính cá nhân"),
    (r"\s+\?", "Lỗi định dạng dấu câu của người gõ (đặt dấu cách trước dấu hỏi)"),
    (r",\s*\.\.\.", "Lỗi định dạng dấu câu tự do (dấu ba chấm liền sau dấu phẩy)")
]

# 2. KHUNG TIÊU ĐỀ CHỨNG MINH TOÁN HỌC & BẤT BIẾN HÌNH THỨC (FORMAL PROOF HEADERS)
# CHỈ áp dụng cho TIÊU ĐỀ BƯỚC CHỨNG MINH ở đầu câu (Proof Step Header) để không bị phạt nhầm là danh sách LLM.
# KHÔNG áp dụng miễn trừ toàn bộ câu văn nếu câu văn đó chứa các liên từ sáo rỗng của AI.
FORMAL_PROOF_HEADER_REGEX: str = (
    r"^(?i)("
    r"phát biểu\s+bất biến(\s+vòng lặp)?(\s+trong)?\s+(pin|pout|inv|bound)\s*\([^\)]*\)|"
    r"(khởi tạo|duy trì|kết thúc|bảo toàn(\s+phần tử)?|hoán vị|đã sắp xếp|giá trị chặn|hàm giảm|bước lặp|điều kiện dừng|điều kiện lặp)|"
    r"(định lý|định lí|bổ đề|hệ quả|mệnh đề|tiên đề|định nghĩa|quy tắc|công thức|phương trình)(\s+[0-9A-Z\.]+)?|"
    r"(chứng minh|lời giải|giải pháp|chứng minh quy nạp|chứng minh phản chứng|bước cơ sở|bước quy nạp|giả thiết quy nạp)|"
    r"(trường hợp|bước)\s+\d+|"
    r"(điều kiện cần|điều kiện đủ|điều kiện cần và đủ)|"
    r"(đầu vào|đầu ra|input|output|precondition|postcondition|tiền điều kiện|hậu điều kiện)"
    r")\s*:"
)

# Biểu thức Toán học / Phương trình thuần túy (Pure Equations)
# Ví dụ: a_n = 1 nếu n = 0, a_n = 6a_{n-1} - 9a_{n-2}, F(n) = O(n log n)
PURE_EQUATION_PATTERNS: List[str] = [
    r"^\s*([a-zA-Z]\s*\[[^\]]+\]|[a-zA-Z]\([a-zA-Z0-9_,\s\+\-]*\))\s*=",
    r"^\s*[a-zA-Z]_[a-zA-Z0-9]+\s*=\s*[^,;]+(\s+nếu\s+.*)?$",
    r"^\s*(\$|\\\(|\\\[).+(\$|\\\)|\\\])\s*$",
    r"^[0-9a-zA-Z\s\(\)\[\]\+\-\*\/\^=<>≤≥,]{3,}\s*(nếu|với|khi)\s+[0-9a-zA-Z\s=<>≤≥,]+$"
]

# 3. NGOẠI LỆ KỸ THUẬT & THUẬT NGỮ CHUYÊN NGÀNH (TECHNICAL ACRONYMS)
TECHNICAL_ACRONYMS: List[str] = [
    r"CVE-\d{4}-\d+",
    r"SYN\s*[-–—>|]+\s*SYN/?ACK\s*[-–—>|]+\s*ACK",
    r"\b(SQLi|XSS|CSRF|SSRF|MitM|DDoS|DoS|ARP|DNS|ICMP|TCP|UDP|HTTP|HTTPS|SSH|RDP)\b",
    r"\b(Elasticsearch|MongoDB|Redis|MySQL|PostgreSQL|Kafka|RabbitMQ)\b",
    r"169\.254\.169\.254",
    r"\b(BERT|GPT|Transformer|ResNet|LSTM|RNN|CNN|Diffusion)\b",
    r"\b(Docker|Kubernetes|CI/CD|DevOps|Microservices|Terraform)\b"
]

# 4. MẪU CÚ PHÁP ĐẶC TRƯNG CỦA MÔ HÌNH NGÔN NGỮ LỚN (GENUINE LLM HALLMARKS)
GENUINE_LLM_SYNTACTIC_PATTERNS: List[Tuple[str, float, str]] = [
    # Cặp liên từ song hành đối xứng nhân tạo
    (
        r"không chỉ\b.{3,80}\bmà còn\b",
        0.35,
        "Cấu trúc song hành đối xứng 'không chỉ... mà còn...' tạo nhịp điệu nhân tạo thường thấy ở LLM"
    ),
    (
        r"vừa\b.{3,60}\bvừa\b",
        0.25,
        "Cấu trúc cân đối vế câu 'vừa... vừa...' mang tính liệt kê dàn trải"
    ),
    (
        r"ở cả\b.{3,60}\blẫn\b",
        0.25,
        "Cấu trúc đối xứng nhị phân 'ở cả... lẫn...'"
    ),
    
    # Mệnh đề chuyển tiếp công thức ở đầu câu
    (
        r"^(bên cạnh đó|ngoài ra|mặt khác|hơn nữa|đồng thời|đáng chú ý là),?\s*",
        0.30,
        "Mở đầu câu bằng từ nối chuyển tiếp công thức, thiếu mạch lập luận tự nhiên"
    ),
    (
        r"\bcó thể thấy rằng\b",
        0.30,
        "Mệnh đề khẳng định mang tính áp đặt ('Có thể thấy rằng...')"
    ),
    (
        r"\bđược (coi|xem|đánh giá|nhận định) là một trong những\b",
        0.35,
        "Cấu trúc bị động hóa phỏng dịch ('is considered to be one of the') làm giảm tính khẳng định khoa học"
    ),
    (
        r"\bđóng (một )?vai trò (vô cùng |hết sức |rất )?(quan trọng|then chốt|cốt lõi|tiên quyết)\b",
        0.35,
        "Tuyên bố cảm tính sáo rỗng về tầm quan trọng thiếu dữ liệu định lượng chứng minh"
    ),
    (
        r"\bkhông thể (phủ nhận|bác bỏ) rằng\b",
        0.35,
        "Lập luận áp đặt công thức ('There is no denying that')"
    ),
    (
        r"\bmở ra (những )?(triển vọng|chân trời|tiềm năng) mới\b",
        0.40,
        "Ẩn dụ sáo rỗng mang phong cách tổng kết của AI"
    ),
    (
        r"\btóm lại, có thể khẳng định rằng\b",
        0.35,
        "Mô thức kết luận rập khuôn của mô hình ngôn ngữ lớn"
    ),
    (
        r"\b(việc|quá trình)\s+(thu thập|xử lý|phân loại|tích hợp|đối chiếu|đánh giá)\s+và\s+(phân tích|triển khai|giám sát|tối ưu hóa)\b",
        0.30,
        "Lạm dụng danh từ hóa chuỗi kép (Extreme Nominalization) làm giảm tính tác động của câu"
    ),
    (
        r"dưới sự phát triển (không ngừng|mạnh mẽ|vượt bậc|chóng mặt) của\b",
        0.35,
        "Lời mở đầu khuôn mẫu sáo rỗng về xu thế công nghệ"
    ),
    (
        r"(ở trên thế giới|toàn cầu) nói chung và (nước ta|việt nam) nói riêng",
        0.30,
        "Cấu trúc so sánh nhị phân công thức 'nói chung... nói riêng'"
    ),
    (
        r"\bmang lại (nhiều )?lợi ích thiết thực\b",
        0.30,
        "Khẳng định định tính sáo rỗng, thiếu dẫn chứng thực nghiệm"
    ),
    (
        r"\bcần có sự kết hợp (hài hòa|chặt chẽ) giữa\b",
        0.30,
        "Lời khuyên chung chung mang tính công thức của LLM"
    ),
    (
        r"\bvấn đề đặt ra ở đây là\b",
        0.30,
        "Cụm từ tạo dẫn dắt giả định điển hình trong văn bản dịch tự động"
    )
]

# 5. DẤU HIỆU ĐỊNH NGHĨA DANH MỤC LLM (TEXTBOOK LISTICLE DEFINITION)
# Nhận diện cấu trúc "Thuật ngữ: Giải thích" của AI mà không nhầm lẫn với Tiêu đề Toán học
LISTICLE_TERM_REGEX: str = r"^([A-ZÀ-Ỹ0-9][^:]{2,45}):\s+([A-ZÀ-Ỹ0-9].{15,})"

LISTICLE_EXPLANATORY_TRIGGERS: List[str] = [
    r"^(là|kỹ thuật|phương pháp|quá trình|hệ thống|việc|cơ chế|công cụ|mô hình|giải pháp|hình thức)\b",
    r"\b(nhằm mục đích|cho phép|được sử dụng để|giúp cho|đóng vai trò)\b",
    r"^(a technique|a method|an approach|a mechanism|refers to|is defined as)\b"
]

