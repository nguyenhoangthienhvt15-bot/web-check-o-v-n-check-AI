import re
from typing import List, Tuple, Set, Dict, Any
from datasketch import MinHash, MinHashLSH

class PlagiarismEngine:
    def __init__(self, threshold: float = 0.4, num_perm: int = 128):
        self.num_perm = num_perm
        self.threshold = threshold
        self.lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        self.corpus_storage: Dict[str, str] = {}
        
        # Nạp dữ liệu mẫu vào cơ sở dữ liệu đối sánh học thuật
        self._seed_reference_corpus()

    def _seed_reference_corpus(self):
        samples = {
            "ref_luanvan_01": (
                "Trí tuệ nhân tạo và học máy đang làm thay đổi căn bản các phương pháp nghiên cứu khoa học. "
                "Quá trình chuyển đổi số trong giáo dục đại học đòi hỏi việc đổi mới toàn diện chương trình đào tạo "
                "và phương pháp giảng dạy. Dữ liệu lớn đóng vai trò then chốt trong việc phân tích hành vi người học "
                "và cá nhân hóa lộ trình tiếp thu kiến thức."
            ),
            "ref_khoahoc_02": (
                "Phát triển bền vững là sự phát triển nhằm thỏa mãn các nhu cầu của hiện tại mà không làm tổn hại đến "
                "khả năng đáp ứng các nhu cầu đó của các thế hệ tương lai. Biến đổi khí hậu đang gây ra những thách thức "
                "nghiêm trọng đối với an ninh lương thực và nguồn tài nguyên nước trên phạm vi toàn cầu."
            ),
            "ref_cntt_03": (
                "Kiến trúc vi dịch vụ (Microservices Architecture) giúp hệ thống phần mềm có khả năng mở rộng cao, "
                "dễ bảo trì và độc lập trong quá trình triển khai. Việc sử dụng message broker như Redis hay RabbitMQ "
                "giúp phân tách các tác vụ xử lý nặng ra khỏi luồng xử lý giao diện người dùng."
            )
        }
        for doc_id, text in samples.items():
            self.index_document(doc_id, text)

    def _tokenize_to_shingles(self, text: str, k: int = 4) -> Set[str]:
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        words = cleaned.split()
        if len(words) < k:
            return {" ".join(words)}
        return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}

    def compute_minhash(self, text: str) -> MinHash:
        m = MinHash(num_perm=self.num_perm)
        shingles = self._tokenize_to_shingles(text)
        for s in shingles:
            m.update(s.encode('utf8'))
        return m

    def index_document(self, doc_id: str, text: str):
        minhash = self.compute_minhash(text)
        try:
            self.lsh.insert(doc_id, minhash)
        except ValueError:
            pass # Tránh trùng key nếu re-index
        self.corpus_storage[doc_id] = text

    def query_similar(self, text: str) -> List[str]:
        minhash = self.compute_minhash(text)
        return self.lsh.query(minhash)

    def calculate_sentence_overlap(self, query_text: str, candidate_text: str) -> Tuple[float, List[Dict[str, Any]]]:
        query_sentences = [s.strip() for s in re.split(r'[.!?\n]+', query_text) if len(s.strip()) > 10]
        cand_words = set(re.findall(r'\b\w+\b', candidate_text.lower()))
        
        matched_sentences = []
        for s in query_sentences:
            s_words = set(re.findall(r'\b\w+\b', s.lower()))
            if not s_words:
                continue
            # Tính Jaccard overlap giữa câu và văn bản nguồn
            intersection = s_words.intersection(cand_words)
            overlap_ratio = len(intersection) / len(s_words)
            if overlap_ratio >= 0.65:
                matched_sentences.append({
                    "text": s,
                    "overlap_ratio": round(overlap_ratio * 100, 1),
                    "type": "exact" if overlap_ratio >= 0.85 else "paraphrase"
                })
                
        similarity_ratio = len(matched_sentences) / max(len(query_sentences), 1)
        return round(similarity_ratio, 4), matched_sentences
