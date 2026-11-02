"""
SYNAPES IP QUOTA & MONETIZATION TIER MANAGER (STRICT PERSISTENCE ENGINE)
Quản lý hạn mức sử dụng (2 lượt miễn phí / IP) và phân hạng gói dịch vụ (Gói 1: 3.000đ, Gói 2: 10.000đ).
Dữ liệu lưu trữ bền vững trên đĩa tại storage/ip_quotas.json với cơ chế fsync và auto-reload.
"""

import os
import json
import time
from typing import Dict, Any, Optional

class QuotaManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QuotaManager, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self):
        self._quotas: Dict[str, Dict[str, Any]] = {}
        # app/core/quota_manager.py -> app/core -> app -> root
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(curr_dir)
        root_dir = os.path.dirname(app_dir)
        
        # Tạo thư mục storage ở cả app/storage và /app/storage
        storage_dir = os.path.join(app_dir, "storage")
        os.makedirs(storage_dir, exist_ok=True)
        self._db_path = os.path.join(storage_dir, "ip_quotas.json")
        
        # Dự phòng thêm đường dẫn cấp root nếu có
        self._backup_db_path = os.path.join(root_dir, "storage", "ip_quotas.json")
        try:
            os.makedirs(os.path.dirname(self._backup_db_path), exist_ok=True)
        except Exception:
            pass

        self._load_from_disk()

    def _load_from_disk(self):
        """Tải dữ liệu mới nhất từ đĩa vào bộ nhớ"""
        loaded = False
        for path in [self._db_path, self._backup_db_path]:
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            self._quotas.update(data)
                            loaded = True
                            break
            except Exception as e:
                print(f"[QuotaManager] Lỗi đọc {path}: {e}")
        return loaded

    def _save_to_disk(self):
        """Ghi đồng bộ bền vững ra đĩa với fsync"""
        paths = [self._db_path]
        if hasattr(self, '_backup_db_path') and self._backup_db_path:
            paths.append(self._backup_db_path)

        for p in paths:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(self._quotas, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
            except Exception as e:
                print(f"[QuotaManager] Lỗi ghi {p}: {e}")

    def get_record(self, ip: str) -> Dict[str, Any]:
        """Lấy bản ghi hạn mức của IP (tự động nạp mới từ đĩa)"""
        self._load_from_disk()
        clean_ip = (ip or "127.0.0.1").strip()
        if clean_ip not in self._quotas:
            self._quotas[clean_ip] = {
                "ip": clean_ip,
                "free_used": 0,
                "paid_tier": 0,      # 0: Free, 1: Gói 3.000đ, 2: Gói 10.000đ
                "paid_credits": 0,   # Số lượt kiểm tra trả phí còn lại
                "history": [],
                "created_at": time.time()
            }
            self._save_to_disk()
        return self._quotas[clean_ip]

    def get_quota_status(self, ip: str) -> Dict[str, Any]:
        """Tính toán trạng thái hạn mức và quyền truy cập hiện tại của IP"""
        rec = self.get_record(ip)
        free_used = rec.get("free_used", 0)
        paid_tier = rec.get("paid_tier", 0)
        paid_credits = rec.get("paid_credits", 0)
        free_remaining = max(0, 2 - free_used)
        can_scan = (free_remaining > 0) or (paid_credits > 0)
        active_tier = paid_tier if paid_credits > 0 else 0

        return {
            "ip": rec.get("ip", ip),
            "free_used": free_used,
            "free_remaining": free_remaining,
            "paid_tier": paid_tier,
            "paid_credits": paid_credits,
            "active_tier": active_tier,
            "can_scan": can_scan,
            "tier_name": "Gói 2 (10.000đ - Chuyên gia)" if active_tier == 2 else ("Gói 1 (3.000đ - Tiêu chuẩn)" if active_tier == 1 else "Bản Miễn Phí (Free)")
        }

    def consume_scan(self, ip: str) -> Dict[str, Any]:
        """
        Khấu trừ NGAY LẬP TỨC 1 lượt kiểm tra cho IP tại thời điểm tải tài liệu lên.
        Ưu tiên trừ lượt trả phí (paid_credits) trước, sau đó mới trừ lượt miễn phí (free_used).
        Nếu đã hết cả 2 -> Từ chối yêu cầu và yêu cầu thanh toán.
        """
        rec = self.get_record(ip)
        paid_credits = rec.get("paid_credits", 0)
        paid_tier = rec.get("paid_tier", 0)
        free_used = rec.get("free_used", 0)

        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.gmtime(time.time() + 7 * 3600))

        # 1. Trường hợp có lượt trả phí (Gói 1 hoặc Gói 2)
        if paid_credits > 0:
            tier_used = paid_tier
            rec["paid_credits"] = paid_credits - 1
            if rec["paid_credits"] <= 0:
                rec["paid_tier"] = 0
            rec.setdefault("history", []).append({
                "action": "CONSUME_SCAN",
                "type": "PAID",
                "tier": tier_used,
                "time": now_str
            })
            self._save_to_disk()
            print(f"[QuotaManager] Đã trừ 1 lượt trả phí (Gói {tier_used}) của IP: {ip}. Còn lại: {rec['paid_credits']}")
            return {
                "allowed": True,
                "tier_used": tier_used,
                "type": "PAID",
                "credits_remaining": rec["paid_credits"],
                "quota": self.get_quota_status(ip)
            }

        # 2. Trường hợp dùng lượt miễn phí (tối đa 2 lượt)
        if free_used < 2:
            rec["free_used"] = free_used + 1
            free_rem = 2 - rec["free_used"]
            rec.setdefault("history", []).append({
                "action": "CONSUME_SCAN",
                "type": "FREE",
                "tier": 0,
                "free_remaining": free_rem,
                "time": now_str
            })
            self._save_to_disk()
            print(f"[QuotaManager] Đã trừ 1 lượt miễn phí của IP: {ip}. Còn lại: {free_rem}/2")
            return {
                "allowed": True,
                "tier_used": 0,
                "type": "FREE",
                "free_remaining": free_rem,
                "quota": self.get_quota_status(ip)
            }

        # 3. Đã hết sạch hạn mức
        print(f"[QuotaManager] IP {ip} đã hết sạch hạn mức (free_used: {free_used}, paid_credits: 0). Chặn kiểm tra!")
        return {
            "allowed": False,
            "reason": "EXHAUSTED_FREE_QUOTA",
            "message": "Địa chỉ IP của bạn đã sử dụng hết 2 lượt kiểm tra miễn phí. Vui lòng thanh toán gói cước để tiếp tục.",
            "quota": self.get_quota_status(ip)
        }

    def grant_package(self, ip: str, package_id: int, tx_id: str = "", amount: int = 0) -> Dict[str, Any]:
        """
        Cấp 1 lượt sử dụng cho gói trả phí (Gói 1 hoặc Gói 2) sau khi ĐÃ XÁC THỰC THÀNH CÔNG THANH TOÁN.
        """
        rec = self.get_record(ip)
        rec["paid_tier"] = package_id
        rec["paid_credits"] = 1
        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.gmtime(time.time() + 7 * 3600))
        rec.setdefault("history", []).append({
            "action": "PURCHASE_PACKAGE",
            "package": package_id,
            "amount": amount,
            "tx_id": tx_id,
            "time": now_str
        })
        self._save_to_disk()
        print(f"[QuotaManager] ĐÃ CẤP QUYỀN IP {ip} -> Gói {package_id} (Số tiền: {amount}đ, TX: {tx_id})")
        return self.get_quota_status(ip)

quota_manager = QuotaManager()
