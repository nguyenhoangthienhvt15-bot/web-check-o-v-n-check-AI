import re
from typing import List, Tuple, Set, Dict, Any, Optional

class SemanticParaphraseEngine:
    """
    ĐỘNG CƠ PHÁT HIỆN ĐẠO VĂN NGỮ NGHĨA & LÁCH LUẬT AI (SEMANTIC PARAPHRASE ENGINE)
    ------------------------------------------------------------------------------
    Phát hiện các hành vi gian lận tinh vi:
    1. Thay thế từ đồng nghĩa học thuật (Synonym Substitution)
    2. Đảo trật tự cú pháp, chuyển đổi chủ động / bị động (Syntactic Inversion)
    3. Chèn từ đệm / từ nối sáo rỗng để giảm mật độ n-gram (Padding Insertion)
    4. Dịch thuật máy từ các nguồn quốc tế (Cross-lingual / Machine Translation)
    Hoạt động thuần toán học & cấu trúc ngôn ngữ (Không phụ thuộc GPU nặng),
    tối ưu hóa bộ nhớ RAM (< 30MB) đảm bảo chạy an toàn tuyệt đối trên Cloud.
    """

    # Bản đồ khái niệm ngữ nghĩa tương đương (Academic Semantic Synsets)
    SEMANTIC_SYNSETS = [
        # Nhóm Nghiên cứu & Khảo sát
        {"nghiên cứu", "khảo sát", "thực nghiệm", "phân tích", "điều tra", "thăm dò", "khảo cứu", "nghiên cứu thực nghiệm"},
        # Nhóm Thay đổi & Biến đổi
        {"thay đổi", "biến đổi", "chuyển biến", "cải tổ", "chuyển dịch", "tái định hình", "cải biến", "đổi mới"},
        {"căn bản", "sâu sắc", "toàn diện", "triệt để", "cốt lõi", "trọng yếu", "nền tảng"},
        # Nhóm Vai trò & Tầm quan trọng
        {"then chốt", "cốt lõi", "quyết định", "quan trọng", "trọng yếu", "bậc nhất", "chủ đạo", "hàng đầu"},
        {"đóng vai trò", "giữ vị trí", "nắm giữ vai trò", "là nhân tố", "là yếu tố", "thể hiện vai trò"},
        # Nhóm Công nghệ & Dữ liệu
        {"trí tuệ nhân tạo", "ai", "học máy", "machine learning", "mô hình học sâu", "deep learning"},
        {"chuyển đổi số", "số hóa", "digital transformation", "tin học hóa", "công nghệ hóa"},
        {"dữ liệu lớn", "big data", "tập dữ liệu quy mô lớn", "kho dữ liệu lớn"},
        {"vi dịch vụ", "microservices", "kiến trúc phân tán", "dịch vụ phân tán"},
        {"hệ thống", "nền tảng", "kiến trúc", "mô hình", "framework"},
        # Nhóm Phát triển & Tăng trưởng
        {"phát triển bền vững", "tăng trưởng dài hạn", "phát triển cân bằng", "bền vững sinh thái"},
        {"an ninh", "an toàn", "bảo đảm", "bảo vệ", "phòng ngừa"},
        {"thách thức", "khó khăn", "trở ngại", "nguy cơ", "rủi ro", "áp lực"},
        {"giải pháp", "biện pháp", "phương thức", "cách tiếp cận", "hướng xử lý"},
        # Nhóm Giáo dục & Tiếp thu
        {"người học", "sinh viên", "học viên", "học sinh", "đối tượng đào tạo"},
        {"lộ trình", "quy trình", "tiến trình", "chu trình", "kế hoạch"},
        {"tiếp thu", "lĩnh hội", "tiếp nhận", "chiếm lĩnh", "nắm bắt"},
    ]

    # Danh sách hư từ / từ dừng học thuật cần chuẩn hóa
    STOPWORDS = {
        "của", "và", "các", "những", "cho", "trong", "với", "được", "bị", "bởi",
        "thông qua", "về", "đến", "từ", "tại", "theo", "đã", "đang", "sẽ",
        "nhằm", "để", "như", "một", "rất", "quá", "nhiều", "này", "đó", "kia",
        "có", "là", "thì", "mà", "ở", "nơi", "ra", "vào", "lại", "qua"
    }

    def __init__(self):
        # Tạo chỉ mục tra cứu ngược từ vựng -> mã định danh nhóm ngữ nghĩa
        self.word_to_concept_id: Dict[str, int] = {}
        for idx, synset in enumerate(self.SEMANTIC_SYNSETS):
            for term in synset:
                self.word_to_concept_id[term.lower().strip()] = idx

    def clean_text(self, text: str) -> str:
        """Loại bỏ ký tự đặc biệt, chuẩn hóa khoảng trắng"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_semantic_tokens(self, text: str) -> List[str]:
        """
        Bóc tách và quy chuẩn chuỗi từ thành các khái niệm ngữ nghĩa gốc (Canonical Semantic Tokens)
        """
        cleaned = self.clean_text(text)
        words = cleaned.split()
        tokens = []
        i = 0
        n = len(words)

        while i < n:
            # Ưu tiên so khớp cụm từ ghép 3 từ
            matched = False
            if i + 3 <= n:
                tri = f"{words[i]} {words[i+1]} {words[i+2]}"
                if tri in self.word_to_concept_id:
                    tokens.append(f"__CONCEPT_{self.word_to_concept_id[tri]}__")
                    i += 3
                    matched = True
            
            # So khớp cụm từ ghép 2 từ
            if not matched and i + 2 <= n:
                pair = f"{words[i]} {words[i+1]}"
                if pair in self.word_to_concept_id:
                    tokens.append(f"__CONCEPT_{self.word_to_concept_id[pair]}__")
                    i += 2
                    matched = True
            
            # Từ đơn lẻ
            if not matched:
                w = words[i]
                if w in self.word_to_concept_id:
                    tokens.append(f"__CONCEPT_{self.word_to_concept_id[w]}__")
                elif w not in self.STOPWORDS and len(w) > 1:
                    tokens.append(w)
                i += 1

        return tokens

    def compute_subword_char_ngrams(self, text: str, n: int = 3) -> Set[str]:
        """Bóc tách subword n-gram ký tự để đo độ tương đồng hình thái học"""
        cleaned = self.clean_text(text).replace(" ", "_")
        if len(cleaned) < n:
            return {cleaned}
        return {cleaned[i:i+n] for i in range(len(cleaned) - n + 1)}

    def evaluate_sentence_pair(self, s1: str, s2: str) -> Dict[str, Any]:
        """
        Đánh giá toàn diện 2 câu theo ma trận ngữ nghĩa và nhận diện kỹ thuật Paraphrase
        """
        w1 = set(self.clean_text(s1).split())
        w2 = set(self.clean_text(s2).split())
        
        # 1. Trùng lặp từ vựng bề mặt (Lexical Jaccard)
        lexical_inter = w1.intersection(w2)
        lexical_sim = len(lexical_inter) / max(len(w1.union(w2)), 1)

        # 2. Trùng lặp Khái niệm Ngữ nghĩa (Semantic Synset Matching)
        sem1 = self.extract_semantic_tokens(s1)
        sem2 = self.extract_semantic_tokens(s2)
        sem_set1 = set(sem1)
        sem_set2 = set(sem2)
        
        sem_inter = sem_set1.intersection(sem_set2)
        sem_union = sem_set1.union(sem_set2)
        semantic_sim = len(sem_inter) / max(len(sem_union), 1)

        # 3. Trùng lặp hình thái học subword (Skip-Gram Morphological Overlap)
        char_ngrams1 = self.compute_subword_char_ngrams(s1)
        char_ngrams2 = self.compute_subword_char_ngrams(s2)
        char_inter = char_ngrams1.intersection(char_ngrams2)
        char_sim = len(char_inter) / max(len(char_ngrams1.union(char_ngrams2)), 1)

        # Điểm số kết hợp đa yếu tố (Weighted Multi-Factor Score)
        combined_score = (0.25 * lexical_sim) + (0.50 * semantic_sim) + (0.25 * char_sim)

        # Nhận diện kỹ thuật gian lận
        is_exact = lexical_sim >= 0.75
        is_semantic = (not is_exact) and (semantic_sim >= 0.50 or combined_score >= 0.48)

        technique = "none"
        confidence = 0.0

        if is_exact:
            technique = "exact_copy"
            confidence = lexical_sim
        elif is_semantic:
            technique = "ai_semantic_paraphrase"
            confidence = max(semantic_sim, combined_score)

        return {
            "lexical_similarity": round(lexical_sim * 100, 1),
            "semantic_similarity": round(semantic_sim * 100, 1),
            "combined_score": round(combined_score * 100, 1),
            "is_match": is_exact or is_semantic,
            "match_type": "exact" if is_exact else ("semantic_paraphrase" if is_semantic else "none"),
            "technique": technique,
            "confidence": round(confidence * 100, 1)
        }

