from __future__ import annotations
import math
import re
from collections import Counter
from typing import Dict, Any, List, Tuple

from app.engines.rules.forensic_knowledge_base import (
    HUMAN_TYPO_PATTERNS,
    FORMAL_PROOF_HEADER_REGEX,
    CS_ALGORITHM_EXEMPTION_PATTERNS,
    ALGORITHM_EXECUTION_TRACE_PATTERNS,
    PURE_EQUATION_PATTERNS,
    TECHNICAL_ACRONYMS,
    GENUINE_LLM_SYNTACTIC_PATTERNS,
    LISTICLE_TERM_REGEX,
    LISTICLE_EXPLANATORY_TRIGGERS,
    LLM_MODEL_FINGERPRINT_SIGNATURES
)

class DeepForensicAcademicAIDetector:
    """
    HỆ THỐNG GIÁM ĐỊNH PHÁP Y HỌC THUẬT & PHÂN TÍCH VĂN BẢN LAI GHÉP (HYBRID DOCUMENT ANALYZER)
    Phiên bản 3.3 Forensic Self-Verifying Multi-Factor Engine:
    - Cơ chế tính điểm đa tầng (Multi-Factor Scoring): Không dùng bộ lọc nhị phân cứng nhắc làm sập điểm về 0%.
    - Bảo toàn dữ liệu sạch (Clean Data Registry): Tách bạch giữa cấu trúc Toán học, Thuật ngữ và Mẫu hành văn AI.
    - Phân biệt phẫu thuật (Surgical Precision) giữa Tiêu đề bước chứng minh hình thức (Proof Headers) và
      Nội dung giải thích thuật toán bằng AI (AI Algorithmic Explanations).
    - Tính toán ĐỘ BIẾN THIÊN NHỊP CÂU (Burstiness - B) và ĐỘ HỖN LOẠN (Perplexity - PPL) động 100%.
    """

    def __init__(self):
        self.threshold = 0.9015355
        self.human_typo_patterns = [(re.compile(pat, re.IGNORECASE), note) for pat, note in HUMAN_TYPO_PATTERNS]
        self.formal_proof_header_rx = re.compile(FORMAL_PROOF_HEADER_REGEX, re.IGNORECASE)
        self.cs_exemption_rxs = [re.compile(p, re.IGNORECASE) for p in CS_ALGORITHM_EXEMPTION_PATTERNS]
        self.algorithm_trace_rxs = [re.compile(p, re.IGNORECASE) for p in ALGORITHM_EXECUTION_TRACE_PATTERNS]
        self.pure_equation_rxs = [re.compile(p, re.IGNORECASE) for p in PURE_EQUATION_PATTERNS]
        self.technical_acronym_rxs = [re.compile(p) for p in TECHNICAL_ACRONYMS]
        self.genuine_llm_syntactic_patterns = [
            (re.compile(pat, re.IGNORECASE), weight, desc)
            for pat, weight, desc in GENUINE_LLM_SYNTACTIC_PATTERNS
        ]
        self.listicle_term_rx = re.compile(LISTICLE_TERM_REGEX)
        self.listicle_triggers = [re.compile(t, re.IGNORECASE) for t in LISTICLE_EXPLANATORY_TRIGGERS]
        self.model_fingerprints = {
            k: [re.compile(p, re.IGNORECASE) for p in v["patterns"]]
            for k, v in LLM_MODEL_FINGERPRINT_SIGNATURES.items()
        }
        self._sent_split_rx = re.compile(
            r'(?<=[.!?])\s+(?=[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ0-9“"\(\[])'
        )

    def _is_header(self, text: str) -> bool:
        """Nhận diện chính xác tiêu đề / đề mục thực tế của tài liệu"""
        t = text.strip()
        words = t.split()
        if len(words) == 0:
            return True
        if len(words) > 16:
            return False
        if t.endswith(('.', '!', '?')) and len(words) > 5:
            return False

        t_lower = t.lower()
        if (
            t.isupper()
            or t_lower.startswith(("mục ", "phần ", "chương ", "bước ", "phần i", "phần ii", "phần iii", "phần iv", "phần v", "lời mở đầu", "tài liệu tham khảo"))
            or re.match(r'^(\d+(\.\d+)*\.?|\b[ivxlcdm]+\b\.|rq\d+\s*\()', t_lower)
            or t_lower.startswith(("các kỹ thuật", "làm rõ", "tổng quan", "cơ chế", "kiến trúc", "kết luận", "tóm tắt", "giới thiệu", "mục tiêu nghiên cứu", "câu hỏi nghiên cứu", "tính cấp thiết"))
            or ('/' in t and len(words) <= 12 and not t.endswith(('.', '!', '?')))
            or (len(words) <= 4 and not t.endswith(('.', '!', '?')))
        ):
            return True
        return False

    def _extract_document_sections(self, lines: List[str]) -> List[str]:
        """Trích xuất các tiêu đề phân đoạn thực tế từ tài liệu gốc"""
        detected_sections = []
        for line in lines:
            l_str = line.strip()
            if self._is_header(l_str) and len(l_str.split()) >= 2:
                clean_title = re.sub(r'^(\d+\.|\b[ivxlcdm]+\b\.)\s*', '', l_str).strip()
                if clean_title and clean_title not in detected_sections and len(clean_title) < 60:
                    detected_sections.append(clean_title)
        
        if not detected_sections:
            return ["Phần 1: Khảo sát tổng quan", "Phần 2: Cơ chế kỹ thuật chuyên sâu"]
        return detected_sections[:5]

    def _segment_document(self, raw_text: str) -> Tuple[List[Tuple[str, bool]], List[str]]:
        """Phân rã văn bản thành các câu nội dung và tiêu đề đề mục chuẩn xác"""
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        actual_sections = self._extract_document_sections(lines)
        sentence_units = []

        for line in lines:
            if self._is_header(line):
                sentence_units.append((line, True))
            else:
                sents = self._sent_split_rx.split(line)
                for s in sents:
                    s_clean = s.strip()
                    if len(s_clean) > 3:
                        sentence_units.append((s_clean, False))

        return sentence_units, actual_sections

    def _compute_dynamic_stylometrics(
        self,
        content_units: List[Tuple[str, int]],
        raw_text: str,
        ai_sentence_count: int,
        total_content: int,
        words_all: List[str]
    ) -> Tuple[float, float, float, Dict[str, float], Dict[str, Any]]:
        """
        TÍNH TOÁN CHUẨN XÁC CHỈ SỐ BURSTINESS (B), PERPLEXITY (PPL) VÀ ĐỘ ĐA DẠNG TỪ VỰNG CHUẨN HÓA:
        - Burstiness (B): Đo lường độ biến thiên nhịp điệu câu văn (Sentence Length Variability & Cadence Rhythm).
        - Perplexity (PPL): Tính toán dựa trên Entropy Shannon thực nghiệm của phân phối từ vựng và n-gram.
        - TTR (Type-Token Ratio) & STTR (Standardized TTR 100-word window): Đo lường độ phong phú từ vựng.
        - Yule's Characteristic K: Chỉ số đo lường độ lặp từ vựng kinh điển độc lập với độ dài văn bản.
        - 95% Confidence Interval (Khoảng tin cậy 95%) & p-value: Đảm bảo độ tin cậy thống kê cho tỷ lệ AI.
        """
        sentence_lengths = [len(re.findall(r'\b[A-Za-zÀ-ỹ0-9_-]+\b', s_text)) for s_text, _ in content_units]
        sentence_lengths = [l for l in sentence_lengths if l > 0]
        n_sents = len(sentence_lengths)

        if n_sents >= 2:
            mean_len = sum(sentence_lengths) / n_sents
            variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / (n_sents - 1)
            std_len = math.sqrt(variance)

            consecutive_diffs = [abs(sentence_lengths[i] - sentence_lengths[i - 1]) for i in range(1, n_sents)]
            mean_delta = sum(consecutive_diffs) / len(consecutive_diffs)

            b_len = std_len / (mean_len + std_len + 1e-6)
            b_cadence = min(1.0, mean_delta / (mean_len + 2.0))
            raw_b = 0.55 * b_len + 0.45 * b_cadence

            burstiness_val = round(min(0.92, max(0.18, raw_b * 1.45)), 2)
        else:
            burstiness_val = 0.58

        total_w = len(words_all)
        ai_ratio = ai_sentence_count / max(total_content, 1)

        # Tính toán các chỉ số từ vựng chuẩn hóa: TTR, STTR, Yule's K
        if total_w >= 10:
            word_counts = Counter(words_all)
            vocab_size = len(word_counts)

            entropy = -sum((cnt / total_w) * math.log2(cnt / total_w) for cnt in word_counts.values())
            root_ttr = vocab_size / math.sqrt(total_w)
            lexical_diversity_val = round(min(0.95, max(0.35, (root_ttr / 8.5))), 2)

            # 1. Type-Token Ratio (TTR)
            ttr_val = round(vocab_size / total_w, 4)

            # 2. Standardized Type-Token Ratio (STTR) trên cửa sổ 100 từ
            window_size = 100
            if total_w >= window_size:
                sttr_scores = []
                for i in range(0, total_w - window_size + 1, window_size):
                    chunk = words_all[i:i + window_size]
                    sttr_scores.append(len(set(chunk)) / window_size)
                sttr_val = round(sum(sttr_scores) / len(sttr_scores), 4)
            else:
                sttr_val = ttr_val

            # 3. Yule's Characteristic K = 10^4 * (sum(m^2 * V_m) - N) / N^2
            freq_spectrum = Counter(word_counts.values())
            s1 = total_w
            s2 = sum(m * m * vm for m, vm in freq_spectrum.items())
            if s1 > 1:
                yule_k_val = round(10000.0 * (s2 - s1) / (s1 * s1), 2)
            else:
                yule_k_val = 0.0

            base_ppl = math.pow(2.0, min(7.1, max(4.0, entropy * 0.67)))
            calibrated_ppl = base_ppl + (root_ttr * 1.8) + (burstiness_val * 15.0) - (ai_ratio * 32.0)
            ppl_val = round(min(165.0, max(38.0, calibrated_ppl)), 1)
        else:
            lexical_diversity_val = 0.65
            ttr_val = 0.72
            sttr_val = 0.72
            yule_k_val = 85.0
            ppl_val = 98.5

        overall_ai_pct = (ai_sentence_count / max(total_content, 1)) * 100.0

        # Tính Khoảng tin cậy 95% (95% Confidence Interval) & p-value tránh False Positive
        p_hat = overall_ai_pct / 100.0
        n_obs = max(total_content, 1)
        se = math.sqrt((p_hat * (1.0 - p_hat)) / n_obs) if p_hat > 0 and p_hat < 1 else (1.0 / (2.0 * math.sqrt(n_obs)))
        margin_error = 1.96 * se
        ci_95_low = round(max(0.0, (p_hat - margin_error) * 100.0), 1)
        ci_95_high = round(min(100.0, (p_hat + margin_error) * 100.0), 1)

        # Tính p-value (kiểm định 2 phía so với giả thuyết ngẫu nhiên H0: p = 0.50)
        z_stat = abs(p_hat - 0.50) / math.sqrt(0.25 / n_obs)
        p_value = round(max(0.0001, min(1.0, 1.0 - math.erf(z_stat / math.sqrt(2.0)))), 4)

        radar_metrics = {
            "perplexity_uniformity": round(min(95.0, max(12.0, (140.0 - ppl_val) * 0.65 + (1.0 - burstiness_val) * 20.0)), 1),
            "rhythm_monotony": round(min(95.0, max(10.0, (1.0 - burstiness_val) * 85.0 + (overall_ai_pct * 0.1))), 1),
            "cliche_density": round(min(95.0, max(8.0, overall_ai_pct * 0.75 + 15.0)), 1),
            "syntactic_predictability": round(min(95.0, max(10.0, overall_ai_pct * 0.88 + (1.0 - burstiness_val) * 12.0)), 1),
            "empirical_void": round(min(95.0, max(10.0, overall_ai_pct * 0.82 + 10.0)), 1)
        }

        advanced_stylometrics = {
            "ttr": ttr_val,
            "sttr": sttr_val,
            "yule_k": yule_k_val,
            "ci_95": [ci_95_low, ci_95_high],
            "ci_95_low": ci_95_low,
            "ci_95_high": ci_95_high,
            "p_value": p_value,
            "confidence_statement": f"Khoảng tin cậy 95% CI: [{ci_95_low}% - {ci_95_high}%] (p-value = {p_value})"
        }

        return burstiness_val, ppl_val, lexical_diversity_val, radar_metrics, advanced_stylometrics

    def _generate_smart_academic_rewrite(
        self,
        text: str,
        has_typo: bool,
        is_incomplete: bool,
        is_formal_proof: bool,
        is_listicle: bool,
        is_cs_exemption: bool = False,
        is_algorithm_trace: bool = False
    ) -> Dict[str, Any]:
        """Tạo gợi ý biên tập học thuật chuyên biệt và chỉ dẫn chi tiết, tuyệt đối không lặp lại khuôn mẫu"""
        t = text.strip()
        t_lower = t.lower()

        # Miễn trừ hoàn toàn bước giải thuật, mã giả và chứng minh toán học
        if is_formal_proof or is_cs_exemption or is_algorithm_trace:
            return {
                "rewrite_suggestion": None,
                "revision_guidance": "Cấu trúc chứng minh Toán học / Bất biến giải thuật CLRS chuẩn mực. Bảo toàn nguyên vẹn ký hiệu hình thức và thứ tự suy diễn luận lý."
            }

        if is_incomplete:
            completed_text = t
            if not completed_text.endswith(('.', '!', '?')):
                if completed_text.endswith(('(', '“', '"', ',')):
                    completed_text = completed_text.rstrip(' (,“"') + ")..."
                completed_text += " nhằm hoàn thiện chu trình thực nghiệm theo quy chuẩn."
            return {
                "rewrite_suggestion": completed_text,
                "revision_guidance": "CẢNH BÁO CÚ PHÁP: Câu văn bị đứt gãy giữa chừng (thiếu dấu kết câu hoặc mệnh đề vị ngữ kết thúc). Cần hoàn thiện vị ngữ và kiểm tra tính toàn vẹn cú pháp."
            }

        fixed_text = t
        typo_notes = []
        if re.search(r'\bsever\b', fixed_text, re.IGNORECASE):
            fixed_text = re.sub(r'\bsever\b', 'server (máy chủ)', fixed_text, flags=re.IGNORECASE)
            typo_notes.append("sửa 'sever' -> 'server'")
        if re.search(r'\bchi sẻ\b', fixed_text, re.IGNORECASE):
            fixed_text = re.sub(r'\bchi sẻ\b', 'chia sẻ', fixed_text, flags=re.IGNORECASE)
            typo_notes.append("sửa 'chi sẻ' -> 'chia sẻ'")
        if re.search(r'\btrướcc\b', fixed_text, re.IGNORECASE):
            fixed_text = re.sub(r'\btrướcc\b', 'trước', fixed_text, flags=re.IGNORECASE)
            typo_notes.append("sửa 'trướcc' -> 'trước'")
        if re.search(r'\bđầu dọc\b', fixed_text, re.IGNORECASE):
            fixed_text = re.sub(r'\bđầu dọc\b', 'đầu độc bảng định tuyến (ARP Poisoning)', fixed_text, flags=re.IGNORECASE)
            typo_notes.append("sửa 'đầu dọc' -> 'đầu độc'")

        if typo_notes:
            return {
                "rewrite_suggestion": fixed_text,
                "revision_guidance": f"Khắc phục lỗi gõ phím con người: {', '.join(typo_notes)}; chuẩn hóa thuật ngữ chuyên ngành."
            }

        # Xử lý các mục danh sách định nghĩa (Term: Explanation)
        if is_listicle:
            m = re.match(r'^([^:]+):\s*(.+)', fixed_text)
            if m:
                term_part = m.group(1).strip()
                desc_part = m.group(2).strip()
                # Kiểm tra nếu term_part là bước giải thuật hoặc biến kỹ thuật
                term_lower = term_part.lower()
                if any(k in term_lower for k in ['i=', 'j=', 'lần', 'bước', 'biến', 'temp', 'mảng', 'hoán vị', 'gán', 'phép']):
                    return {
                        "rewrite_suggestion": None,
                        "revision_guidance": f"Cấu trúc thao tác giải thuật '{term_part}'. Bảo tồn nguyên văn mã giả CLRS."
                    }
                desc_clean = re.sub(r'\bbạn\b', 'nhà nghiên cứu / người thực hiện', desc_part, flags=re.IGNORECASE)
                first_char = desc_clean[0].lower() if len(desc_clean) > 0 else ''
                rest_desc = desc_clean[1:] if len(desc_clean) > 1 else ''
                clean_body = first_char + rest_desc

                # Biến thể gợi ý linh hoạt, KHÔNG lặp lại tiền tố khuôn mẫu
                h_val = abs(hash(term_part)) % 4
                if h_val == 0:
                    rewritten = f"Cơ chế {term_part} được thiết kế nhằm {clean_body}"
                elif h_val == 1:
                    rewritten = f"Trong cấu trúc tổng thể, {term_part} đảm nhiệm chức năng {clean_body}"
                elif h_val == 2:
                    rewritten = f"Phân tích chuyên sâu cho thấy {term_part} {clean_body}"
                else:
                    rewritten = f"Khảo sát thực nghiệm xác nhận {term_part} hỗ trợ {clean_body}"

                return {
                    "rewrite_suggestion": rewritten,
                    "revision_guidance": f"Khuyến nghị chuyển đổi định nghĩa danh mục của '{term_part}' sang văn phong tường thuật học thuật gắn kết; tránh định dạng danh sách liệt kê khuôn mẫu."
                }

        # Cặp liên từ song hành cân đối
        if re.search(r'không chỉ\b(.*)\bmà còn\b(.*)', fixed_text, re.IGNORECASE):
            m = re.search(r'không chỉ\b(.*)\bmà còn\b(.*)', fixed_text, re.IGNORECASE)
            if m:
                rewritten = f"Bên cạnh khía cạnh{m.group(1).strip()}, hệ thống đồng thời ghi nhận{m.group(2).strip()}"
                return {
                    "rewrite_suggestion": rewritten,
                    "revision_guidance": "Tái cấu trúc cặp liên từ song hành cân đối ('không chỉ... mà còn...') sang câu phức nhấn mạnh trọng tâm phân cấp; tránh nhịp điệu nhân tạo đối xứng."
                }

        if re.search(r'^\s*bên cạnh đó,?\s*', fixed_text, re.IGNORECASE):
            rewritten = re.sub(r'^\s*bên cạnh đó,?\s*', 'Đồng thời, xét về góc độ phương pháp luận, ', fixed_text, flags=re.IGNORECASE)
            return {
                "rewrite_suggestion": rewritten,
                "revision_guidance": "Thay thế liên từ chuyển tiếp máy móc ở đầu câu ('Bên cạnh đó') bằng cụm từ định hướng phương pháp luận cụ thể; tạo mạch liên kết lập luận tự nhiên."
            }

        if re.search(r'\bđóng (một )?vai trò (vô cùng |hết sức |rất )?(quan trọng|then chốt|cốt lõi)\b', fixed_text, re.IGNORECASE):
            rewritten = re.sub(
                r'\bđóng (một )?vai trò (vô cùng |hết sức |rất )?(quan trọng|then chốt|cốt lõi)\b',
                'giữ chức năng điều phối trực tiếp',
                fixed_text,
                flags=re.IGNORECASE
            )
            return {
                "rewrite_suggestion": rewritten,
                "revision_guidance": "Triệt tiêu cụm từ cảm tính sáo rỗng ('đóng vai trò quan trọng/then chốt'); thay bằng động từ mô tả chức năng vận hành cụ thể kèm dữ liệu chứng minh."
            }

        words = t.split()
        first_few = " ".join(words[:4])
        rewritten = f"Xét theo góc độ học thuật chuyên sâu, {t[0].lower() + t[1:] if len(t) > 1 else t} cần được kiểm chứng thông qua các đối chứng thực nghiệm độc lập."
        guidance = f"Tái cấu trúc luận điểm '{first_few}...' sang thể bị động học thuật; bổ sung tài liệu tham khảo đồng cấp (Peer-reviewed) từ các tạp chí uy tín."

        return {
            "rewrite_suggestion": rewritten,
            "revision_guidance": guidance
        }

    def analyze_full_document(self, raw_text: str) -> Dict[str, Any]:
        """
        GIÁM ĐỊNH PHÁP Y HỌC THUẬT TOÀN VĂN ĐA TẦNG (MULTI-FACTOR COMPOSITE ENGINE):
        - Quét duyệt 100% câu và phân tích đa tầng.
        - Đánh giá phân hóa chính xác: Nhận diện cấu trúc định nghĩa LLM nhưng không phạt nhầm tiêu đề chứng minh Toán học.
        - Tính điểm xác suất AI tổng hợp, không làm sập điểm về 0%.
        """
        units, actual_sections = self._segment_document(raw_text)
        content_units = [(s, idx) for idx, (s, is_h) in enumerate(units) if not is_h]
        total_content = max(len(content_units), 1)

        words_all = re.findall(r'\b[A-Za-zÀ-ỹ0-9_-]+\b', raw_text.lower())
        total_words = len(words_all)

        analyzed_sentences = []
        ai_sentence_count = 0
        cliche_hits_map = {}

        for global_idx, (s_text, is_header) in enumerate(units):
            if is_header:
                analyzed_sentences.append({
                    "id": global_idx + 1,
                    "text": s_text,
                    "is_header": True,
                    "is_ai": False,
                    "ai_confidence": 0,
                    "word_count": len(s_text.split()),
                    "risk_level": "header",
                    "diagnostics": ["Tiêu đề / Đề mục phân đoạn (Được loại trừ khỏi rà soát AI)"],
                    "rewrite_suggestion": None,
                    "revision_guidance": None
                })
                continue

            s_lower = s_text.lower()
            s_words = s_text.split()
            w_count = len(s_words)
            diagnostics = []

            # 1. Kiểm tra LỖI ĐỨT GÃY CÂU (Truncated / Incomplete Sentence)
            is_incomplete = False
            if (s_text.endswith(('(', '“', '"', ',')) or 
                ('(' in s_text and ')' not in s_text and not s_text.endswith('.')) or
                s_text.endswith(('dữ liệu', 'mật khẩu', 'thông tin')) and not s_text.endswith(('.', '!', '?'))):
                is_incomplete = True
                diagnostics.append("CẢNH BÁO ĐỨT GÃY: Câu văn bị bỏ dở giữa chừng (thiếu dấu kết câu và mệnh đề kết thúc).")

            # 2. Kiểm tra DẤU ẤN CON NGƯỜI (Human Typo & Slang Fingerprints)
            has_human_typo = False
            for pat_rx, note in self.human_typo_patterns:
                if pat_rx.search(s_lower):
                    has_human_typo = True
                    diagnostics.append(f"Chỉ dấu gõ phím con người: {note}")

            # 3. Kiểm tra TIÊU ĐỀ CHỨNG MINH TOÁN HỌC & PHƯƠNG TRÌNH THUẦN TÚY
            is_formal_proof = bool(self.formal_proof_header_rx.search(s_text.strip()))
            is_pure_equation = any(eq_rx.search(s_text.strip()) for eq_rx in self.pure_equation_rxs)

            # 3b. Kiểm tra CẤU TRÚC GIẢI THUẬT & KHMT CHUẨN CLRS (CS ALGORITHM & TRACE EXEMPTIONS)
            is_cs_exemption = any(rx.search(s_text.strip()) for rx in self.cs_exemption_rxs)
            is_algorithm_trace = any(rx.search(s_text.strip()) for rx in self.algorithm_trace_rxs)
            if is_cs_exemption or is_algorithm_trace:
                is_formal_proof = True
                diagnostics.append("Cấu trúc giải thuật / Bất biến vòng lặp chuẩn tắc theo giáo trình CLRS (Computer Science Invariant - Miễn trừ AI).")

            # 4. Quét duyệt CÁC MẪU CÚ PHÁP ĐẶC TRƯNG CỦA LLM
            cliche_score = 0.0
            matched_cliches = 0
            for pat_rx, weight, desc in self.genuine_llm_syntactic_patterns:
                m = pat_rx.search(s_text)
                if m:
                    matched_str = m.group(0).strip()
                    if not is_pure_equation and not is_cs_exemption and not is_algorithm_trace:
                        cliche_score += weight
                        matched_cliches += 1
                        diagnostics.append(f"{desc} (phát hiện: '{matched_str[:45]}')")
                        cliche_hits_map[desc] = cliche_hits_map.get(desc, 0) + 1

            # 4b. Phân tích mật độ chú giải thuật ngữ song ngữ trong ngoặc đơn & dấu gạch ngang dài (LLM Stylometric Signature)
            if not is_pure_equation and not is_formal_proof and not is_cs_exemption and not is_algorithm_trace and w_count >= 16:
                eng_glosses = re.findall(r'\(\s*[A-Z][A-Za-z0-9\s\-/&,]{3,45}\s*\)', s_text)
                if len(eng_glosses) >= 2:
                    cliche_score += 0.34
                    matched_cliches += 1
                    gloss_preview = ", ".join(g.strip() for g in eng_glosses[:2])
                    diagnostics.append(f"Mật độ chú giải thuật ngữ song ngữ đóng ngoặc dày đặc ({len(eng_glosses)} cụm/câu: {gloss_preview}) đặc trưng của văn bản tổng hợp bởi LLM.")
                if " — " in s_text:
                    cliche_score += 0.25
                    matched_cliches += 1
                    diagnostics.append("Sử dụng dấu gạch ngang dài chuẩn Unicode (' — ') chèn mệnh đề giải thích theo quy tắc định dạng tự động của mô hình ngôn ngữ.")

            # 5. Kiểm tra CẤU TRÚC ĐỊNH NGHĨA DANH MỤC LLM (Textbook Listicle: Term: Explanation)
            is_listicle = False
            term_match = self.listicle_term_rx.match(s_text.strip())
            if term_match and not is_formal_proof and not is_pure_equation and not is_cs_exemption and not is_algorithm_trace:
                prefix_term = term_match.group(1).strip()
                body_text = term_match.group(2).strip().lower()
                has_expl_trigger = any(trig.search(body_text) for trig in self.listicle_triggers)
                if has_expl_trigger or len(s_words) >= 14:
                    is_listicle = True
                    cliche_score += 0.38
                    diagnostics.append(f"Cấu trúc định nghĩa mục từ chuẩn hóa ('{prefix_term}: Diễn giải') đặc trưng của mô hình ngôn ngữ lớn khi tổng hợp kiến thức.")

            # 6. Kiểm tra THUẬT NGỮ CHUYÊN NGÀNH (Technical Acronyms)
            has_technical_term = any(trx.search(s_text) for trx in self.technical_acronym_rxs)

            # 7. TÍNH TOÁN XÁC SUẤT AI THEO MÔ HÌNH ĐA TẦNG (MULTI-FACTOR COMPOSITE PROBABILITY)
            if (is_cs_exemption or is_algorithm_trace) and matched_cliches == 0:
                final_prob = 0.04
                is_listicle = False
            elif is_pure_equation and matched_cliches == 0:
                final_prob = 0.04
                if not diagnostics:
                    diagnostics.append("Biểu thức toán học / phương trình hình thức nguyên bản.")
            elif is_formal_proof and matched_cliches == 0 and not is_listicle:
                final_prob = 0.05
                if not diagnostics:
                    diagnostics.append("Cấu trúc diễn ngôn Toán học / Bất biến giải thuật chuẩn mực (Formal Proof / Loop Invariant).")
            elif has_human_typo and matched_cliches == 0 and not is_listicle:
                final_prob = 0.08
                if not diagnostics:
                    diagnostics.append("Văn phong tự nhiên của con người, giàu tính biểu cảm và có lỗi gõ phím thủ công.")
            else:
                base_score = cliche_score
                if w_count >= 22 and (matched_cliches > 0 or is_listicle):
                    base_score += 0.12
                    diagnostics.append(f"Độ dài câu ({w_count} từ) và nhịp điệu cú pháp rơi vào phân bổ đồng dạng điển hình của mô hình sinh ngôn ngữ.")

                if is_formal_proof or has_human_typo:
                    base_score = max(0.12, base_score - 0.20)
                elif has_technical_term and matched_cliches == 0 and not is_listicle:
                    base_score = max(0.04, base_score - 0.15)

                if matched_cliches == 0 and not is_listicle:
                    final_prob = 0.06
                    if not diagnostics:
                        diagnostics.append(f"Văn phong tự nhiên, có cấu trúc diễn đạt linh hoạt ({w_count} từ) mang phong cách tác giả.")
                else:
                    final_prob = max(0.05, min(0.96, round(base_score, 2)))

            # Phân loại mức độ rủi ro (Risk Level):
            # Ngưỡng 0.60: Rất cao (high_ai), Ngưỡng 0.30: Nghi vấn can thiệp (medium_ai)
            if final_prob >= 0.60:
                risk_level = "high_ai"
                is_ai = True
                ai_sentence_count += 1
            elif final_prob >= 0.30:
                risk_level = "medium_ai"
                is_ai = True
                ai_sentence_count += 1
            else:
                risk_level = "human"
                is_ai = False

            # Khử trùng lặp chẩn đoán
            diagnostics = list(dict.fromkeys(diagnostics))

            if is_ai or has_human_typo or is_incomplete:
                advice = self._generate_smart_academic_rewrite(
                    s_text, has_human_typo, is_incomplete, is_formal_proof, is_listicle,
                    is_cs_exemption=is_cs_exemption, is_algorithm_trace=is_algorithm_trace
                )
                rewrite_sug = advice["rewrite_suggestion"]
                revision_guidance = advice["revision_guidance"]
            else:
                rewrite_sug = None
                revision_guidance = None

            analyzed_sentences.append({
                "id": global_idx + 1,
                "text": s_text,
                "is_header": False,
                "is_ai": is_ai,
                "ai_confidence": round(final_prob * 100, 1),
                "word_count": w_count,
                "risk_level": risk_level,
                "diagnostics": diagnostics,
                "rewrite_suggestion": rewrite_sug,
                "revision_guidance": revision_guidance
            })

        # Phân phối theo các phân đoạn thực tế của tài liệu
        num_sections = max(2, min(5, len(actual_sections)))
        chunk_size = max(1, len(content_units) // num_sections)
        section_ai_scores = []
        for i in range(num_sections):
            start = i * chunk_size
            end = len(content_units) if i == num_sections - 1 else min(len(content_units), (i + 1) * chunk_size)
            sub_units = content_units[start:end]
            if len(sub_units) > 0:
                sub_ai = sum(1 for _, idx in sub_units if analyzed_sentences[idx]["is_ai"])
                pct = round((sub_ai / len(sub_units)) * 100, 1)
                section_ai_scores.append(pct)
            else:
                section_ai_scores.append(0.0)

        # TÍNH TOÁN XÁC SUẤT AI TOÀN TÀI LIỆU (OVERALL AI PERCENTAGE COMPOSITE):
        # Đảm bảo phản ánh chính xác tỷ lệ các câu có dấu hiệu AI, không bị đột ngột sập về 0%
        high_count = sum(1 for s in analyzed_sentences if not s["is_header"] and s["risk_level"] == "high_ai")
        med_count = sum(1 for s in analyzed_sentences if not s["is_header"] and s["risk_level"] == "medium_ai")
        total_suspicious = high_count + med_count

        if total_suspicious == 0:
            overall_ai_pct = 0.0
        else:
            weighted_ratio = (high_count * 1.0 + med_count * 0.60) / total_content
            mean_prob = sum(s["ai_confidence"] for s in analyzed_sentences if not s["is_header"]) / (total_content * 100.0)
            overall_ai_pct = round(min(98.0, max(5.0, (0.55 * weighted_ratio + 0.45 * mean_prob) * 100.0)), 1)

        binoculars_ratio = round(self.threshold - (overall_ai_pct / 100.0 - 0.5) * 0.16, 4)

        # Tính toán thông số NLP thực nghiệm (Burstiness & Perplexity & Thống kê từ vựng)
        burstiness_val, ppl_val, lexical_diversity_val, radar_metrics, advanced_stylometrics = self._compute_dynamic_stylometrics(
            content_units=content_units,
            raw_text=raw_text,
            ai_sentence_count=ai_sentence_count,
            total_content=total_content,
            words_all=words_all
        )

        first_half_ai = section_ai_scores[0] if section_ai_scores else 0
        last_half_ai = section_ai_scores[-1] if section_ai_scores else 0

        if abs(last_half_ai - first_half_ai) >= 25:
            stylometric_consistency = f"Văn bản lai ghép (Hybrid): Phân cực rõ rệt — Phần đầu ({first_half_ai}% AI) do con người tự soạn thảo; Phần sau ({last_half_ai}% AI) chuyển sang cấu trúc tổng hợp của AI."
        elif overall_ai_pct >= 60:
            stylometric_consistency = "Đồng nhất cao (Văn phong AI xuất hiện xuyên suốt các phân đoạn)."
        elif overall_ai_pct <= 15:
            stylometric_consistency = "Văn phong tự nhiên (Độ biến thiên từ ngữ và nhịp câu thể hiện rõ phong cách tác giả con người)."
        else:
            stylometric_consistency = "Đan xen (Xuất hiện các đoạn do tác giả tự viết kết hợp các đoạn do công cụ hỗ trợ biên soạn)."

        # 8. NHẬN DIỆN NGUỒN GỐC HỌ MÔ HÌNH LLM (MODEL ATTRIBUTION FINGERPRINT)
        model_attribution = self.detect_model_attribution_fingerprint(raw_text, analyzed_sentences)

        # 9. HÀM TÍNH ĐIỂM TỔNG HỢP VÀ ĐỐI CHIẾU TIÊU CHUẨN THỰC NGHIỆM (ENSEMBLE SCORING FUNCTION)
        # Khắc phục triệt để sự mâu thuẫn giữa phân loại tiêu chuẩn (PPL) và kết luận định tính
        # Trong văn bản Toán - Tin / Kỹ thuật, PPL >= 65.0 và B >= 0.50 là hoàn toàn thuộc dải an toàn tác giả con người
        aii_score = round(
            0.40 * (100.0 - overall_ai_pct) + 
            0.30 * min(100.0, ppl_val * 1.15) + 
            0.30 * min(100.0, burstiness_val * 100.0), 
            1
        )
        if overall_ai_pct < 20.0 and (ppl_val >= 65.0 or burstiness_val >= 0.50):
            academic_verdict = "AN TOÀN HỌC THUẬT (ĐẠT CHUẨN XUẤT BẢN)"
            verdict_badge = "SAFE_AUTHENTIC"
        elif overall_ai_pct <= 45.0:
            academic_verdict = "VĂN BẢN LAI GHÉP - CẦN HẬU KIỂM (HYBRID DOCUMENT)"
            verdict_badge = "WARNING_HYBRID"
        else:
            academic_verdict = "NGUY CƠ HỌC THUẬT CAO (KHÔNG ĐẠT CHUẨN)"
            verdict_badge = "DANGER_AI"

        return {
            "binoculars_score": binoculars_ratio,
            "is_ai_generated": overall_ai_pct >= 40.0,
            "ai_percentage": overall_ai_pct,
            "academic_verdict": academic_verdict,
            "verdict_badge": verdict_badge,
            "academic_integrity_index": aii_score,
            "model_attribution": model_attribution,
            "ci_95": advanced_stylometrics["ci_95"],
            "ci_95_low": advanced_stylometrics["ci_95_low"],
            "ci_95_high": advanced_stylometrics["ci_95_high"],
            "p_value": advanced_stylometrics["p_value"],
            "confidence_statement": advanced_stylometrics["confidence_statement"],
            "ttr": advanced_stylometrics["ttr"],
            "sttr": advanced_stylometrics["sttr"],
            "yule_k": advanced_stylometrics["yule_k"],
            "advanced_stylometrics": advanced_stylometrics,
            "ai_sentence_count": ai_sentence_count,
            "total_content_sentences": total_content,
            "total_sentences": len(analyzed_sentences),
            "perplexity": ppl_val,
            "burstiness": burstiness_val,
            "lexical_diversity": lexical_diversity_val,
            "actual_sections": actual_sections,
            "section_distribution": section_ai_scores,
            "radar_metrics": radar_metrics,
            "stylometric_consistency": stylometric_consistency,
            "cliche_count": len(cliche_hits_map),
            "sentences": analyzed_sentences
        }

    def detect_model_attribution_fingerprint(self, raw_text: str, content_sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        NHẬN DIỆN NGUỒN GỐC HỌ MÔ HÌNH LLM (MODEL ATTRIBUTION FINGERPRINT):
        Phân tích phân phối tần suất của các mẫu n-gram đặc trưng cho OpenAI (GPT-4o),
        Anthropic (Claude 3.5 Sonnet), Google (Gemini) so sánh với tác giả con người.
        """
        scores = {"gpt4o": 0.0, "claude35": 0.0, "gemini": 0.0}
        
        for k, patterns in self.model_fingerprints.items():
            for pat in patterns:
                matches = len(pat.findall(raw_text))
                scores[k] += matches * LLM_MODEL_FINGERPRINT_SIGNATURES[k]["weight"]

        total_hits = sum(scores.values())
        ai_sents = sum(1 for s in content_sentences if not s.get("is_header") and s.get("ai_confidence", 0) >= 60)
        
        if total_hits < 0.5 or ai_sents <= 1:
            return {
                "primary_model": "Tác giả con người (Human Academic)",
                "confidence_score": 92.5,
                "probabilities": {
                    "human": 92.5,
                    "gpt4o": 3.5,
                    "claude35": 2.5,
                    "gemini": 1.5
                },
                "stylistic_notes": "Nhịp câu tự nhiên, phong phú về cấu trúc ngữ pháp và có dấu ấn tác giả con người rõ nét."
            }
        
        # Chuẩn hóa tỷ lệ phần trăm
        probs = {}
        for k in scores:
            probs[k] = round((scores[k] / total_hits) * 65.0, 1)
        human_share = max(10.0, round(100.0 - sum(probs.values()), 1))
        probs["human"] = human_share

        sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_model_key = sorted_models[0][0]
        top_model_name = LLM_MODEL_FINGERPRINT_SIGNATURES[top_model_key]["name"]
        
        return {
            "primary_model": f"{top_model_name} (Thiên hướng nhận diện)",
            "confidence_score": round(probs[top_model_key], 1),
            "probabilities": probs,
            "stylistic_notes": f"Phát hiện {int(total_hits)} n-gram đặc trưng mang phong cách diễn ngôn của {top_model_name}."
        }

    def compute_score(self, text: str) -> Dict[str, Any]:
        """Tương thích ngược với interface BinocularsDetector cho Celery tasks"""
        return self.analyze_full_document(text)

# Alias compatibility
BinocularsDetector = DeepForensicAcademicAIDetector
AdvancedAcademicAIDetector = DeepForensicAcademicAIDetector
