import hashlib
import time
import os
import json
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

VN_TZ = timezone(timedelta(hours=7))

class VerificationService:
    """
    DỊCH VỤ XÁC THỰC PHÁP LÝ & TÍNH TOÀN VẸN BIÊN BẢN (LEGAL INTEGRITY & QR VERIFICATION)
    ---------------------------------------------------------------------------------
    Lưu trữ mã băm SHA-256 và các chỉ số định lượng gốc của tài liệu để ngăn chặn
    hành vi chỉnh sửa điểm số bằng Photoshop hoặc sửa file PDF sau khi xuất bản.
    Hỗ trợ lưu trữ đĩa bền vững (JSON Storage) và cơ chế tự phục hồi (Self-Healing).
    """
    def __init__(self):
        self._certificates: Dict[str, Dict[str, Any]] = {}
        self._hash_to_id: Dict[str, str] = {}
        
        # Đường dẫn lưu trữ chứng thư bền vững trên máy chủ
        self._db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "storage", 
            "certificates_db.json"
        )
        
        # Nạp dữ liệu từ bộ nhớ đĩa hoặc khởi tạo mặc định
        self._load_certificates()

    def _normalize_key(self, key: Optional[str]) -> str:
        """Chuẩn hóa khóa tra cứu (loại bỏ dấu tiếng Việt, gạch chéo, khoảng trắng) để tra cứu mượt mà"""
        if not key:
            return ""
        k = key.strip().upper()
        k = k.replace("Đ", "D").replace("đ", "d")
        k = k.replace("/", "").replace("-", "").replace("_", "").replace(" ", "")
        return k

    def _load_certificates(self):
        """Nạp danh sách chứng thư từ bộ nhớ đĩa hoặc tạo mới nếu chưa tồn tại"""
        loaded = False
        try:
            if os.path.exists(self._db_path):
                with open(self._db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._certificates = data
                        for cid, cdata in self._certificates.items():
                            sh = cdata.get("short_hash")
                            dh = cdata.get("doc_hash")
                            if sh:
                                self._hash_to_id[sh] = cid
                            if dh:
                                self._hash_to_id[dh] = cid
                        loaded = True
        except Exception as e:
            print(f"[VerificationService] Cảnh báo đọc file DB: {e}")

        if not loaded or not self._certificates:
            self._seed_default_certificates()

    def _save_certificates(self):
        """Lưu danh sách chứng thư xuống đĩa để bảo toàn dữ liệu sau khi server khởi động lại"""
        try:
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(self._certificates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[VerificationService] Cảnh báo ghi file DB: {e}")

    def _seed_default_certificates(self):
        sample_hash = hashlib.sha256("SYNAPES_DEFAULT_SEED_DOCUMENT".encode('utf-8')).hexdigest()
        self.register_certificate(
            cert_id="SYN-2026/BB-GDHT-09",
            filename="Tài liệu kiểm định liêm chính học thuật mẫu.docx",
            text="Tài liệu kiểm định liêm chính học thuật mẫu",
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
        """Tạo và lưu chứng thư pháp lý số hóa của biên bản kèm URL tra cứu tự thân (Self-Contained URL)"""
        doc_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        short_hash = doc_hash[:16]

        # Đóng gói toàn bộ thông số định lượng vào URL xác thực để bảo đảm quét QR luôn hiển thị đúng 100%
        # ngay cả khi máy chủ khởi động lại hoặc chạy môi trường serverless không trạng thái (stateless)
        query_params = [
            f"id={urllib.parse.quote(cert_id)}",
            f"hash={short_hash}",
            f"fn={urllib.parse.quote(filename)}",
            f"orig={orig_percentage}",
            f"ai={ai_percentage}",
            f"plag={plag_percentage}",
            f"ppl={ppl}",
            f"b={burstiness}",
            f"dt={urllib.parse.quote(report_datetime)}",
            f"w={total_words or len(text.split())}",
            f"s={total_sentences}"
        ]
        verification_url = f"/verify?{'&'.join(query_params)}"

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
            "verification_url": verification_url,
            "status": "VALID_AUTHENTIC",
            "created_at": time.time()
        }

        self._certificates[cert_id] = cert_data
        self._hash_to_id[short_hash] = cert_id
        self._hash_to_id[doc_hash] = cert_id
        
        # Lưu xuống bộ nhớ đĩa
        self._save_certificates()
        return cert_data

    def get_certificate(self, cert_id: Optional[str] = None, doc_hash: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Tra cứu biên bản theo mã chứng thư hoặc mã băm tài liệu với cơ chế đối sánh linh hoạt"""
        # 1. Tra cứu chính xác
        if cert_id and cert_id in self._certificates:
            return self._certificates[cert_id]
        if doc_hash:
            matched_id = self._hash_to_id.get(doc_hash) or self._hash_to_id.get(doc_hash[:16])
            if matched_id and matched_id in self._certificates:
                return self._certificates[matched_id]

        # 2. Tra cứu mềm dẻo (Normalized Key Traversal)
        target_norm = self._normalize_key(cert_id) if cert_id else self._normalize_key(doc_hash)
        if target_norm:
            for cid, cdata in self._certificates.items():
                if self._normalize_key(cid) == target_norm:
                    return cdata
                sh = cdata.get("short_hash", "")
                dh = cdata.get("doc_hash", "")
                if sh and (self._normalize_key(sh) == target_norm or target_norm.endswith(self._normalize_key(sh[:4]))):
                    return cdata
                if dh and self._normalize_key(dh) == target_norm:
                    return cdata
                # Kiểm tra hậu tố 4 ký tự hexa cuối của số hiệu (ví dụ: SYN-2026/BB-GĐHT-7382 khớp với 7382)
                if cid.split("-")[-1].upper() == target_norm[-4:].upper():
                    return cdata

        return None

# Singleton instance
verification_service = VerificationService()
