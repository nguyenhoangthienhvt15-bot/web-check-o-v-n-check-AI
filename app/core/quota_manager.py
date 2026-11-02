"""
SYNAPES IP QUOTA & MONETIZATION TIER MANAGER
Quản lý hạn mức sử dụng (2 lượt miễn phí / IP) và phân hạng gói dịch vụ (Gói 1: 3.000đ, Gói 2: 10.000đ).
Dữ liệu lưu trữ bền vững trên đĩa tại app/storage/ip_quotas.json.
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
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        os.makedirs(storage_dir, exist_ok=True)
        self._db_path = os.path.join(storage_dir, "ip_quotas.json")
        self._load_from_disk()

    def _load_from_disk(self):
        try:
            if os.path.exists(self._db_path):
                with open(self._db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._quotas = data
        except Exception as e:
            print(f"[QuotaManager] Lỗi đọc ip_quotas: {e}")

    def _save_to_disk(self):
        try:
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(self._quotas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[QuotaManager] Lỗi ghi ip_quotas: {e}")

    def get_record(self, ip: str) -> Dict[str, Any]:
        if ip not in self._quotas:
            self._quotas[ip] = {
                "ip": ip,
                "free_used": 0,
                "paid_tier": 0,      # 0: Free, 1: Gói 3.000đ, 2: Gói 10.000đ
                "paid_credits": 0,   # Số lượt kiểm tra trả phí còn lại
                "history": [],
                "created_at": time.time()
            }
        return self._quotas[ip]

    def get_quota_status(self, ip: str) -> Dict[str, Any]:
        rec = self.get_record(ip)
        free_used = rec.get("free_used", 0)
        paid_tier = rec.get("paid_tier", 0)
        paid_credits = rec.get("paid_credits", 0)
        free_remaining = max(0, 2 - free_used)
        can_scan = (free_used < 2) or (paid_credits > 0)
        active_tier = paid_tier if paid_credits > 0 else 0

        return {
            "ip": ip,
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
        Ghi nhận tiêu thụ 1 lượt kiểm tra cho IP.
        Ưu tiên dùng lượt trả phí nếu có, sau đó dùng lượt miễn phí.
        Nếu hết cả 2 -> Báo lỗi cần thanh toán.
        """
        rec = self.get_record(ip)
        paid_credits = rec.get("paid_credits", 0)
        paid_tier = rec.get("paid_tier", 0)
        free_used = rec.get("free_used", 0)

        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.gmtime(time.time() + 7 * 3600))

        if paid_credits > 0:
            tier_used = paid_tier
            rec["paid_credits"] = paid_credits - 1
            if rec["paid_credits"] <= 0:
                rec["paid_tier"] = 0
            rec.setdefault("history", []).append({
                "action": "SCAN",
                "type": "PAID",
                "tier": tier_used,
                "time": now_str
            })
            self._save_to_disk()
            return {
                "allowed": True,
                "tier_used": tier_used,
                "type": "PAID",
                "credits_remaining": rec["paid_credits"]
            }

        if free_used < 2:
            rec["free_used"] = free_used + 1
            rec.setdefault("history", []).append({
                "action": "SCAN",
                "type": "FREE",
                "tier": 0,
                "time": now_str
            })
            self._save_to_disk()
            return {
                "allowed": True,
                "tier_used": 0,
                "type": "FREE",
                "free_remaining": 2 - rec["free_used"]
            }

        return {
            "allowed": False,
            "reason": "EXHAUSTED_FREE_QUOTA",
            "message": "Địa chỉ IP của bạn đã sử dụng hết 2 lượt kiểm tra miễn phí. Vui lòng thanh toán gói cước để tiếp tục."
        }

    def grant_package(self, ip: str, package_id: int, tx_id: str = "", amount: int = 0) -> Dict[str, Any]:
        """
        Cấp 1 lượt sử dụng cho gói trả phí (Gói 1 hoặc Gói 2) sau khi xác nhận thanh toán.
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
        print(f"[QuotaManager] Đã cấp quyền IP {ip} -> Gói {package_id} (TX: {tx_id})")
        return self.get_quota_status(ip)

quota_manager = QuotaManager()

