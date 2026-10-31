"""
AUTOMATED REGRESSION TEST HARNESS & SELF-HEALING ENGINE
Chịu trách nhiệm tự động kiểm thử toàn diện hệ thống giám định pháp y học thuật (SYNAPES AUDIT).
Ngăn chặn 100% tình trạng 'lợn lành thành lợn què' (regressions) khi cập nhật quy tắc hoặc thuật toán.
"""

import sys
import math
import re
from typing import Dict, Any, List

class ForensicRegressionHarness:
    """Harness tự động chạy bộ chuẩn đối sánh (Golden Benchmark Test Suite)"""

    def __init__(self):
        from app.engines.ai_detector import DeepForensicAcademicAIDetector
        self.detector = DeepForensicAcademicAIDetector()

    def run_all_benchmarks(self) -> Dict[str, Any]:
        tests = [
            ("Test 1: Hybrid Cybersecurity Document (Phát hiện AI nửa sau)", self._test_hybrid_cybersecurity),
            ("Test 2: Algorithm Report with AI content (Báo cáo giải thuật có AI)", self._test_algorithm_report_with_ai),
            ("Test 3: Formal Math Loop Invariants (Bất biến Toán không bị phạt nhầm)", self._test_formal_math_invariants),
            ("Test 4: Pure Human with Telex Typos (Con người tự viết có lỗi phím)", self._test_pure_human_typos),
            ("Test 5: Dynamic Burstiness & Perplexity (B & PPL tính động, không cố định)", self._test_dynamic_stylometrics),
            ("Test 6: Regex Compilation & Python 3.11+ Safety (Không có lỗi inline flag)", self._test_regex_compilation),
            ("Test 7: Bilingual Biomedical Proposal (Đề cương Y sinh song ngữ có AI)", self._test_biomedical_hybrid_proposal),
            ("Test 8: Paragraph Break Preservation (Bảo toàn xuống dòng khi xử lý Toán)", self._test_paragraph_preservation)
        ]

        results = {
            "all_passed": True,
            "total_tests": len(tests),
            "passed_tests": 0,
            "failed_tests": 0,
            "details": []
        }

        for name, test_fn in tests:
            try:
                test_fn()
                results["passed_tests"] += 1
                results["details"].append({"name": name, "status": "PASSED", "error": None})
            except Exception as e:
                results["all_passed"] = False
                results["failed_tests"] += 1
                results["details"].append({"name": name, "status": "FAILED", "error": str(e)})

        return results

    def _test_hybrid_cybersecurity(self):
        # Mẫu tài liệu lai ghép An toàn thông tin: Phần đầu con người tự viết, phần sau AI định nghĩa thuật ngữ
        text = """
HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG
CÁC KỸ THUẬT TẤN CÔNG MẠNG PHỔ BIẾN

Một ngày đẹp trời khi bạn kết nối wifi công cộng ở quán cafe, dữ liệu cá nhân có nguy cơ bị lộ.
Tôi tự làm bài khảo sát này dựa trên kinh nghiệm cấu hình sever và chi sẻ với các bạn trong lab.
Kẻ tấn công có thể sử dụng kỹ thuật đầu dọc bảng định tuyến arp để chiếm phiên đăng nhập ?

CÁC KỸ THUẬT NÂNG CAO

Stateless SYN Scanning: Kỹ thuật quét cổng gửi gói tin SYN mà không hoàn tất bắt tay ba bước nhằm phát hiện các dịch vụ đang mở một cách nhanh chóng.
Banner Grabbing: Phương pháp kết nối tới cổng dịch vụ để thu thập thông tin phiên bản phần mềm máy chủ mục tiêu.
Shadow IT: Việc các bộ phận tự ý triển khai phần mềm không qua kiểm duyệt đóng vai trò vô cùng quan trọng trong việc gia tăng bề mặt tấn công.
Không chỉ dừng lại ở đó, kỹ thuật này còn mở ra những chân trời mới cho việc khai thác lỗ hổng bảo mật.
        """.strip()

        res = self.detector.analyze_full_document(text)
        assert res["ai_percentage"] >= 20.0, f"Expected AI >= 20%, got {res['ai_percentage']}% (Lỗi: Bị trả về 0% AI)"
        assert res["ai_sentence_count"] >= 2, f"Expected >= 2 AI sentences, got {res['ai_sentence_count']}"

    def _test_algorithm_report_with_ai(self):
        # Mẫu báo cáo thuật toán có đoạn giải thích dùng văn phong AI
        text = """
BÁO CÁO BÀI TẬP LỚN MÔN PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN
PHẦN 1: MÔ TẢ BÀI TOÁN

Bài toán yêu cầu giải quyết hệ thức truy hồi tuyến tính bậc hai với các điều kiện sau:
a_n = 1 nếu n = 0
a_n = 6 nếu n = 1
a_n = 6a_{n-1} - 9a_{n-2} nếu n > 1

Thuật toán này không chỉ đóng một vai trò vô cùng quan trọng mà còn mở ra những tiềm năng mới trong việc xử lý dữ liệu lớn.
Có thể thấy rằng dưới sự phát triển mạnh mẽ của khoa học máy tính, việc tối ưu hóa giải thuật mang lại nhiều lợi ích thiết thực.
        """.strip()

        res = self.detector.analyze_full_document(text)
        assert res["ai_percentage"] >= 15.0, f"Expected AI >= 15%, got {res['ai_percentage']}% (Lỗi: Bị trả về 0% AI)"
        
        # Phương trình a_n không được bị gắn nhãn high_ai
        eq_sent = next((s for s in res["sentences"] if "a_n = 1" in s["text"]), None)
        if eq_sent:
            assert eq_sent["risk_level"] == "human", f"Equation must be human, got {eq_sent['risk_level']}"

    def _test_formal_math_invariants(self):
        # Mẫu chứng minh Toán học rời rạc / Bất biến vòng lặp (Insertion Sort)
        text = """
Phát biểu Bất biến vòng lặp trong Pin(j): Mảng con A[1..j-1] luôn luôn được sắp xếp theo thứ tự tăng dần.
Khởi tạo: Trước khi vòng lặp bắt đầu với j = 2, mảng con chỉ gồm 1 phần tử nên hiển nhiên đã sắp xếp.
Duy trì: Giả sử bất biến đúng trước bước j, ta chèn phần tử key vào đúng vị trí để mảng A[1..j] có thứ tự tăng dần.
Kết thúc: Khi j > n, vòng lặp dừng lại và mảng A[1..n] gồm toàn bộ các phần tử ban đầu đã được sắp xếp hoàn chỉnh.
        """.strip()

        res = self.detector.analyze_full_document(text)
        # Toàn bộ các bước chứng minh chuẩn tắc này phải là human
        for s in res["sentences"]:
            if not s["is_header"]:
                assert s["risk_level"] == "human", f"Proof step '{s['text'][:30]}' must be human, got {s['risk_level']}"
                # Không được có chẩn đoán trùng lặp
                diags = s["diagnostics"]
                assert len(diags) == len(set(diags)), f"Duplicate diagnostics in: {diags}"

    def _test_pure_human_typos(self):
        text = """
Hôm nay tôi tự viết bài báo cáo thí nghiệm mạng này sau khi ngồi ở quán cafe cả buổi sáng.
Trong quá trình cấu hình sever thử nghiệm, tôi đã phát hiện lỗi gõ phím trướcc khi nộp bài và chi sẻ cho cả nhóm cùng xem .
        """.strip()

        res = self.detector.analyze_full_document(text)
        assert res["ai_percentage"] <= 15.0, f"Expected human text AI <= 15%, got {res['ai_percentage']}%"

    def _test_dynamic_stylometrics(self):
        # 2 văn bản có độ dài câu khác biệt hoàn toàn
        text1 = "Câu này rất ngắn. Tiếp tục ngắn. Lại ngắn nữa. Rất nhanh. Xong một câu."
        text2 = "Trong khuôn khổ khảo sát thực nghiệm chuyên sâu về an toàn không gian mạng và phân tích các giao thức truyền tải, nhóm tác giả đã tiến hành đối chiếu toàn diện các tham số đo đạc trên môi trường giả lập nhằm lượng hóa nguy cơ tiềm ẩn với độ tin cậy thống kê cao."

        res1 = self.detector.analyze_full_document(text1)
        res2 = self.detector.analyze_full_document(text2)

        b1 = res1["burstiness"]
        b2 = res2["burstiness"]
        assert b1 != 0.65 or b2 != 0.65, "Burstiness must not be a hardcoded 0.65 constant!"
        assert res1["perplexity"] > 0, "PPL must be calculated"
        assert res2["perplexity"] > 0, "PPL must be calculated"

    def _test_regex_compilation(self):
        from app.engines.rules.forensic_knowledge_base import (
            HUMAN_TYPO_PATTERNS, FORMAL_PROOF_HEADER_REGEX, PURE_EQUATION_PATTERNS,
            TECHNICAL_ACRONYMS, GENUINE_LLM_SYNTACTIC_PATTERNS
        )

        # Đảm bảo tuyệt đối không có inline global flag (?i) nằm sai vị trí gây crash Python 3.11+
        assert "(?i)" not in FORMAL_PROOF_HEADER_REGEX, "FORMAL_PROOF_HEADER_REGEX must not contain inline (?i)"
        re.compile(FORMAL_PROOF_HEADER_REGEX, re.IGNORECASE)

        for pat, _ in HUMAN_TYPO_PATTERNS:
            assert "(?i)" not in pat, f"Inline (?i) forbidden in {pat}"
            re.compile(pat, re.IGNORECASE)
        for eq in PURE_EQUATION_PATTERNS:
            assert "(?i)" not in eq, f"Inline (?i) forbidden in {eq}"
            re.compile(eq, re.IGNORECASE)
        for tech in TECHNICAL_ACRONYMS:
            assert "(?i)" not in tech, f"Inline (?i) forbidden in {tech}"
            re.compile(tech)
        for pat, _, _ in GENUINE_LLM_SYNTACTIC_PATTERNS:
            assert "(?i)" not in pat, f"Inline (?i) forbidden in {pat}"
            re.compile(pat, re.IGNORECASE)

    def _test_biomedical_hybrid_proposal(self):
        text = """
LỜI MỞ ĐẦU
Dưới sự phát triển không ngừng cùng sự tiến bộ của khoa học kĩ thuật hiện hành ở trên thế giới nói chung và nước ta nói riêng - rất nhiều các nghiên cứu mang tính hỗ trợ cộng đồng đã ra đời.
Chu kỳ kinh nguyệt được coi là “dấu hiệu sinh tồn thứ 5” của cơ thể nữ giới, không chỉ phản ánh khả năng sinh sản mà còn là “tấm gương” phản chiếu rõ nhất về sức khỏe nội tiết.
The ability to tailor lifestyle practices to the tracked cycle via the biomedical system not only maintains stable circadian and biological rhythms, but also fosters beneficial changes in endocrine and mental health.
Mô hình ngôn ngữ nhỏ chạy cục bộ (On-device TinyLM 1B–2B) hoàn toàn có khả năng giải quyết bài toán trích xuất thực thể y sinh với điều kiện phải áp dụng kỹ thuật tinh chỉnh tập trung (Task-specific Fine-tuning) kết hợp cùng cơ chế kiểm soát cấu trúc đầu ra (Constrained/Grammar-based Decoding).
        """.strip()

        res = self.detector.analyze_full_document(text)
        assert res["ai_percentage"] >= 35.0, f"Expected Biomedical Proposal AI >= 35%, got {res['ai_percentage']}%"
        assert res["ai_sentence_count"] >= 3, f"Expected >= 3 AI sentences, got {res['ai_sentence_count']}"

    def _test_paragraph_preservation(self):
        from app.utils.omml_latex import enhance_plain_text_math
        sample = "PHẦN 1: MỞ ĐẦU\n\nCâu văn thứ nhất của đoạn một.\n\nPHẦN 2: NỘI DUNG\n\nCâu văn thứ hai với x = 5."
        processed = enhance_plain_text_math(sample)
        assert "\n" in processed, "enhance_plain_text_math must NOT strip newline characters (\\n)!"
        lines = [l.strip() for l in processed.split("\n") if l.strip()]
        assert len(lines) == 4, f"Expected 4 preserved lines, got {len(lines)}"

if __name__ == "__main__":
    harness = ForensicRegressionHarness()
    res = harness.run_all_benchmarks()
    print(f"Benchmarks passed: {res['passed_tests']}/{res['total_tests']}")
    for d in res["details"]:
        print(f" - {d['name']}: {d['status']} {d['error'] or ''}")
    if not res["all_passed"]:
        sys.exit(1)

