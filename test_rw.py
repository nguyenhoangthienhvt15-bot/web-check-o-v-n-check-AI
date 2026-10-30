import sys
sys.path.insert(0, '/app')
from app.engines.ai_detector import DeepForensicAcademicAIDetector

engine = DeepForensicAcademicAIDetector()
test_sents = [
    "Hướng dẫn: Đừng bao giờ vứt bỏ hàm õ(t) sau khi thay số, trừ khi bạn đang",
    "Hướng dẫn bấm máy tính Casio Fx580VNX: Để tránh nhầm lẫn khi tính phi(T), hãy nhập",
    "Dựa trên việc xây dựng dữ liệu và mô hình xử lí chuyên biệt, hệ thống giúp xâu chuỗi lại các tác động và thay đổi trong quá trình theo dõi chu kì kinh nguyệt của phụ nữ...",
    "Sự biến động của các hormone chính (Estrogen, Progesterone, LH, FSH) chi phối trực tiếp hàng loạt hệ thống sinh học khác trong cơ thể người."
]

for s in test_sents:
    res = engine._generate_smart_academic_rewrite(s, False, False)
    print("VĂN BẢN GỐC:")
    print(s)
    print("HƯỚNG DẪN SỬA (Chi tiết):")
    print(res["revision_guidance"])
    print("VĂN BẢN ĐỀ XUẤT:")
    print(res["rewrite_suggestion"])
    print("=" * 60)
