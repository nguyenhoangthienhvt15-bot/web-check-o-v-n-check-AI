import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

VN_TZ = timezone(timedelta(hours=7))

class VerificationService:
    """
    DỊCH VỤ XÁC THỰC PHÁP LÝ & TÍNH TOÀN VẸN BIÊN BẢN (LEGAL INTEGRITY & QR VERIFICATION)
    ---------------------------------------------------------------------------------
    Lưu trữ mã băm SHA-256 và các chỉ số định lượng gốc của tài liệu để ngăn chặn
    hành vi chỉnh sửa điểm số bằng Photoshop hoặc sửa file PDF sau khi xuất bản.
    """
    def __init__(self):
        # Lưu trữ chứng thư theo mã chứng thư hoặc mã băm
        self._certificates: Dict[str, Dict[str, Any]] = {}
        self._hash_to_id: Dict[str, str] = {}
        
        # Khởi tạo một số biên bản chuẩn mực mặc định
        self._seed_default_certificates()

    def _seed_default_certificates(self):
        sample_hash = hashlib.sha256("SYNAPES_DEFAULT_SEED_DOCUMENT".encode('utf-8')).hexdigest()
        self.register_certificate(
            cert_id="SYN-2026/BB-GĐHT-09",
            filename="Bản phác thảo triển khai ý tưởng 2.docx",
            text="Bản phác thảo triển khai ý tưởng 2",
            ai_percentage=0.0,
            plag_percentage=0.0,
            orig_percentage=100.0,
            ppl=111.0,
            burstiness=0.64,
            report_date_vn="ngày 31 tháng 10 năm 2026",
            report_datetime="17:35:00 31/10/2026"
        )

    def register_certificate(
        self,
        cert_id: str,
        filename: str,
        text: str,
        ai_percentage: float,
        plag_percentage: float,
        orig_percentage: float,
        ppl: float,
        burstiness: float,
        report_date_vn: str,
        report_datetime: str,
        total_words: int = 0,
        total_sentences: int = 0
    ) -> Dict[str, Any]:
        """Tạo và lưu chứng thư pháp lý số hóa của biên bản"""
        doc_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        short_hash = doc_hash[:16]

        cert_data = {
            "cert_id": cert_id,
            "filename": filename,
            "doc_hash": doc_hash,
            "short_hash": short_hash,
            "ai_percentage": ai_percentage,
            "plag_percentage": plag_percentage,
            "originality_percentage": orig_percentage,
            "perplexity": ppl,
            "burstiness": burstiness,
            "report_date_vn": report_date_vn,
            "report_datetime": report_datetime,
            "total_words": total_words or len(text.split()),
            "total_sentences": total_sentences,
            "examiner": "KS NGUYỄN HOÀNG THIỆN",
            "title_examiner": "TRƯỞNG BAN CHUYỂN ĐỔI SỐ VÀ TRÍ TUỆ NHÂN TẠO",
            "organization": "TRUNG TÂM GIÁM ĐỊNH PHÁP Y HỌC THUẬT & SỞ HỮU TRÍ TUỆ SYNAPES AUDIT",
            "verification_url": f"/verify?id={cert_id}&hash={short_hash}",
            "status": "VALID_AUTHENTIC",
            "created_at": time.time()
        }

        self._certificates[cert_id] = cert_data
        self._hash_to_id[short_hash] = cert_id
        self._hash_to_id[doc_hash] = cert_id
        return cert_data

    def get_certificate(self, cert_id: Optional[str] = None, doc_hash: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Tra cứu biên bản theo mã chứng thư hoặc mã băm tài liệu"""
        if cert_id and cert_id in self._certificates:
            return self._certificates[cert_id]
        if doc_hash:
            matched_id = self._hash_to_id.get(doc_hash) or self._hash_to_id.get(doc_hash[:16])
            if matched_id and matched_id in self._certificates:
                return self._certificates[matched_id]
        return None

# Singleton instance
verification_service = VerificationService()
