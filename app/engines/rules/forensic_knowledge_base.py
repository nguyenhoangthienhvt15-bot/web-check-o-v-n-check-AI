"""
FORENSIC KNOWLEDGE BASE & CLEAN DATA REGISTRY
Hệ thống lưu trữ và bảo tồn quy tắc giám định pháp y học thuật chuẩn (Golden Ruleset).
Đảm bảo tính bất biến của các tập dữ liệu sạch, ngăn chặn triệt để tình trạng hồi quy (regression)
qua mỗi phiên bản cập nhật. Tuân thủ nghiêm ngặt chuẩn biên dịch Regex của Python 3.11+.
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
# LƯU Ý: Không dùng inline flag (?i) bên trong chuỗi để tương thích tuyệt đối với Python 3.11+ re._parser;
# truyền cờ re.IGNORECASE khi gọi re.compile().
FORMAL_PROOF_HEADER_REGEX: str = r"^(phát biểu\s+bất biến(\s+vòng lặp)?(\s+trong)?\s+(pin|pout|inv|bound)\s*\([^\)]*\)|(khởi tạo|duy trì|kết thúc|bảo toàn(\s+phần tử)?|hoán vị|đã sắp xếp|giá trị chặn|hàm giảm|bước lặp|điều kiện dừng|điều kiện lặp)|(định lý|định lí|bổ đề|hệ quả|mệnh đề|tiên đề|định nghĩa|quy tắc|công thức|phương trình)(\s+[0-9A-Z\.]+)?|(chứng minh|lời giải|giải pháp|chứng minh quy nạp|chứng minh phản chứng|bước cơ sở|bước quy nạp|giả thiết quy nạp)|(trường hợp|bước)\s+\d+|(điều kiện cần|điều kiện đủ|điều kiện cần và đủ)|(đầu vào|đầu ra|input|output|precondition|postcondition|tiền điều kiện|hậu điều kiện))\s*:"

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

# 4. MẪU CÚ PHÁP ĐẶC TRƯNG CỦA MÔ HÌNH NGÔN NGỮ LỚN (GENUINE LLM HALLMARKS - ĐA NGỮ VIỆT & ANH)
GENUINE_LLM_SYNTACTIC_PATTERNS: List[Tuple[str, float, str]] = [
    # Cặp liên từ song hành đối xứng nhân tạo (Tiếng Việt & Tiếng Anh)
    (
        r"không chỉ\b.{3,140}\bmà còn\b",
        0.38,
        "Cấu trúc song hành đối xứng 'không chỉ... mà còn...' tạo nhịp điệu nhân tạo điển hình của LLM"
    ),
    (
        r"\bnot (only|merely)\b.{3,160}\bbut also\b",
        0.42,
        "Cấu trúc song hành đối xứng tiếng Anh 'not only/merely... but also...' đặc trưng của văn bản sinh bởi LLM"
    ),
    (
        r"\bnói chung\s+(và|cùng)\b.{2,70}\bnói riêng\b",
        0.36,
        "Cấu trúc so sánh nhị phân khuôn mẫu 'nói chung... nói riêng' của mô hình ngôn ngữ"
    ),
    (
        r"\bin general\s+and\b.{2,60}\b(in particular|specifically)\b",
        0.36,
        "Cấu trúc đối xứng nhị phân 'in general and... specifically' điển hình của bản dịch AI"
    ),
    (
        r"vừa\b.{3,80}\bvừa\b",
        0.28,
        "Cấu trúc cân đối vế câu 'vừa... vừa...' mang tính liệt kê dàn trải"
    ),
    (
        r"ở cả\b.{3,60}\blẫn\b",
        0.28,
        "Cấu trúc đối xứng nhị phân 'ở cả... lẫn...'"
    ),

    # Mệnh đề mở đầu & chuyển tiếp công thức
    (
        r"dưới sự phát triển (không ngừng|mạnh mẽ|vượt bậc|chóng mặt)\b",
        0.38,
        "Lời mở đầu khuôn mẫu sáo rỗng ('Dưới sự phát triển không ngừng...') đặc trưng của ChatGPT/LLM"
    ),
    (
        r"^(bên cạnh đó|ngoài ra|mặt khác|hơn nữa|đồng thời|đáng chú ý là|ngược lại),?\s*",
        0.32,
        "Mở đầu câu bằng từ nối chuyển tiếp công thức, thiếu mạch lập luận tự nhiên"
    ),
    (
        r"\bcó thể thấy rằng\b",
        0.32,
        "Mệnh đề khẳng định mang tính áp đặt ('Có thể thấy rằng...')"
    ),
    (
        r"\bđược (coi|xem|đánh giá|nhận định) là (một trong những|[“\x22]dấu hiệu)\b",
        0.35,
        "Cấu trúc bị động hóa phỏng dịch ('is considered/regarded as') đặc trưng của AI"
    ),
    (
        r"\b(is regarded as|is considered to be|serves as building)\b",
        0.35,
        "Cấu trúc bị động học thuật khuôn mẫu trong tiếng Anh do LLM tạo sinh"
    ),
    (
        r"\b(tấm gương|primary mirror)\b.{1,35}\b(phản chiếu|reflecting|of endocrine)\b",
        0.34,
        "Ẩn dụ tu từ khuôn mẫu ('tấm gương phản chiếu / primary mirror') của mô hình ngôn ngữ"
    ),
    (
        r"\b(xây dựng một hàng rào phòng vệ|essential health defense barrier)\b",
        0.35,
        "Cụm ẩn dụ công thức ('hàng rào phòng vệ / defense barrier') sinh bởi AI"
    ),

    # Cấu trúc trả lời câu hỏi nghiên cứu (Prompt-Response Echoing & Academic Synthesis)
    (
        r"\bhoàn toàn có khả năng giải quyết bài toán\b",
        0.38,
        "Mệnh đề khẳng định dập khuôn dạng trả lời Prompt ('hoàn toàn có khả năng giải quyết bài toán')"
    ),
    (
        r"\bvới điều kiện phải áp dụng (kỹ thuật|cơ chế|phương pháp)\b",
        0.34,
        "Cấu trúc rào đón điều kiện chuẩn hóa của LLM ('với điều kiện phải áp dụng...')"
    ),
    (
        r"\bgiải quyết căn bản hạn chế của\b",
        0.38,
        "Mẫu câu luận giải mở đầu đoạn văn đặc trưng của LLM ('giải quyết căn bản hạn chế của...')"
    ),
    (
        r"\bbằng cách chuyển dịch từ\b.{3,90}\bsang\b",
        0.36,
        "Cấu trúc đối lập khái niệm 'bằng cách chuyển dịch từ... sang...' mang dấu ấn tổng hợp của AI"
    ),
    (
        r"\b(thông qua \d+ trụ cột|có \d+ khoảng trống nghiên cứu)\b",
        0.36,
        "Cấu trúc đóng khung số lượng luận điểm ('thông qua N trụ cột / N khoảng trống') điển hình của GPT/Claude"
    ),
    (
        r"\b(phân định ranh giới trách nhiệm thuật toán|loại bỏ rủi ro suy diễn lan man)\b",
        0.35,
        "Cụm thuật ngữ khái niệm hóa do LLM biên dịch từ mẫu kiến trúc hệ thống"
    ),
    (
        r"\blà cầu nối giúp\b.{3,80}\b(đưa ra các nhận định|chính xác và kịp thời)\b",
        0.35,
        "Ẩn dụ công thức 'là cầu nối giúp... chính xác và kịp thời' thường gặp trong văn bản AI"
    ),
    (
        r"\bsự bất cân xứng về\b.{3,50}\bvà giá trị nhận lại\b",
        0.34,
        "Cấu trúc danh từ hóa đối xứng ('sự bất cân xứng về... và giá trị nhận lại')"
    ),
    (
        r"\b(fosters beneficial changes|healthy habit-forming solution)\b",
        0.34,
        "Cụm từ vựng tiếng Anh tổng hợp mang phong cách diễn đạt đặc trưng của LLM"
    ),

    # Mẫu câu sáo rỗng & Danh từ hóa cực độ (Extreme Nominalization)
    (
        r"\bđóng (một )?vai trò (vô cùng |hết sức |rất |như một )?(quan trọng|then chốt|cốt lõi|tiên quyết|bằng chứng)\b",
        0.35,
        "Tuyên bố khuôn mẫu về vai trò ('đóng vai trò quan trọng/then chốt/như một bằng chứng')"
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
        r"\b(việc|quá trình)\s+(thu thập|xử lý|phân loại|tích hợp|đối chiếu|đánh giá|trích xuất)\s+và\s+(phân tích|triển khai|giám sát|tối ưu hóa|chuẩn hóa)\b",
        0.32,
        "Lạm dụng danh từ hóa chuỗi kép (Extreme Nominalization) làm giảm tính tác động của câu"
    ),
    (
        r"\bmang lại (nhiều )?(lợi ích|giá trị) (thiết thực|thực tế)\b",
        0.32,
        "Khẳng định định tính sáo rỗng, thiếu dẫn chứng thực nghiệm"
    ),
    (
        r"\bcần có sự kết hợp (hài hòa|chặt chẽ) giữa\b",
        0.32,
        "Lời khuyên chung chung mang tính công thức của LLM"
    ),
    (
        r"\bvấn đề đặt ra ở đây là\b",
        0.32,
        "Cụm từ tạo dẫn dắt giả định điển hình trong văn bản dịch tự động"
    )
]

# 5. DẤU HIỆU ĐỊNH NGHĨA DANH MỤC LLM (TEXTBOOK LISTICLE DEFINITION)
# Nhận diện cấu trúc "Thuật ngữ: Giải thích" của AI mà không nhầm lẫn với Tiêu đề Toán học
LISTICLE_TERM_REGEX: str = r"^([A-ZÀ-Ỹ0-9][^:]{2,45}):\s+([A-ZÀ-Ỹ0-9].{15,})"

LISTICLE_EXPLANATORY_TRIGGERS: List[str] = [
    r"^(là|kỹ thuật|phương pháp|quá trình|hệ thống|việc|cơ chế|công cụ|mô hình|giải pháp|hình thức|mô hình ngôn ngữ|công cụ chuỗi)\b",
    r"\b(nhằm mục đích|cho phép|được sử dụng để|giúp cho|đóng vai trò|hoàn toàn có khả năng|giải quyết căn bản)\b",
    r"^(a technique|a method|an approach|a mechanism|refers to|is defined as)\b"
]
