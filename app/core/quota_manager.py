"""
SYNAPES IP QUOTA & MONETIZATION TIER MANAGER (STRICT PERSISTENCE & ANTI-RESET ENGINE)
Quản lý hạn mức sử dụng (2 lượt miễn phí / IP) và phân hạng gói dịch vụ (Gói 1: 3.000đ, Gói 2: 10.000đ).
Dữ liệu lưu trữ bền vững trên đĩa tại storage/ip_quotas.json kết hợp đồng bộ trạng thái bất biến (Monotonic State Sync)
giúp bảo toàn 100% hạn mức ngay cả sau khi cập nhật trang web hoặc khởi động lại container.
"""

import os
import json
import time
from typing import Dict, Any, Optional

# Các mã email giao dịch lịch sử trước đây được khóa cố định để không bao giờ bị khớp nhầm
HISTORICAL_CONSUMED_MSG_IDS = {
    "1a19d225b7010982",
    "1a19d73da05e83c6",
    "1a19db4af552e7cf",
    "1a19f9f34234bfd5",
    "1a19fc3a5e7965ac",
    "1a19fc49a32b0fb4",
    "1a19fc523c819565",
    "1a1a006133d2f22b",
    "1a19f9f30daa6108",
    "1a19fc3a139c02fd",
    "1a19fc4974b49801",
    "1a19fc51e1b0d814",
    "1a1a006164b72039"
}


class QuotaManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QuotaManager, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self):
        self._quotas: Dict[str, Any] = {
            "_consumed_tx": {mid: {"status": "HISTORICAL_LOCKED"} for mid in HISTORICAL_CONSUMED_MSG_IDS},
            "_exhausted_tx": {}
        }
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(curr_dir)
        root_dir = os.path.dirname(app_dir)

        storage_dir = os.path.join(app_dir, "storage")
        os.makedirs(storage_dir, exist_ok=True)
        self._db_path = os.path.join(storage_dir, "ip_quotas.json")

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
                            for k, v in data.items():
                                if k in ("_consumed_tx", "_exhausted_tx") and isinstance(v, dict):
                                    self._quotas.setdefault(k, {}).update(v)
                                else:
                                    self._quotas[k] = v
                            loaded = True
                            break
            except Exception as e:
                print(f"[QuotaManager] Lỗi đọc {path}: {e}")
        # Đảm bảo các ID lịch sử luôn nằm trong _consumed_tx
        consumed = self._quotas.setdefault("_consumed_tx", {})
        for mid in HISTORICAL_CONSUMED_MSG_IDS:
            consumed.setdefault(mid, {"status": "HISTORICAL_LOCKED"})
        self._quotas.setdefault("_exhausted_tx", {})
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

    def is_tx_consumed(self, msg_id: str) -> bool:
        """Kiểm tra xem email giao dịch Timo (theo Gmail Message ID) đã được cấp cho IP nào chưa"""
        self._load_from_disk()
        clean_id = (msg_id or "").strip().lower()
        if not clean_id:
            return True
        consumed = self._quotas.get("_consumed_tx", {})
        return (clean_id in consumed) or (msg_id in consumed)

    def mark_tx_consumed(self, msg_id: str, ip: str, package_id: int, amount: int):
        """Khóa vĩnh viễn Gmail Message ID cho địa chỉ IP vừa xác nhận thành công"""
        self._load_from_disk()
        clean_id = (msg_id or "").strip().lower()
        consumed = self._quotas.setdefault("_consumed_tx", {})
        consumed[clean_id] = {
            "ip": ip,
            "package": package_id,
            "amount": amount,
            "consumed_at": int(time.time() * 1000)
        }
        self._save_to_disk()

    def get_record(self, ip: str) -> Dict[str, Any]:
        """Lấy bản ghi hạn mức của IP (tự động nạp mới từ đĩa)"""
        self._load_from_disk()
        clean_ip = (ip or "127.0.0.1").strip()
        if clean_ip not in self._quotas or not isinstance(self._quotas[clean_ip], dict):
            self._quotas[clean_ip] = {
                "ip": clean_ip,
                "free_used": 0,
                "paid_tier": 0,      # 0: Free, 1: Gói 3.000đ, 2: Gói 10.000đ
                "paid_credits": 0,   # Số lượt kiểm tra trả phí còn lại
                "last_tx_id": "",
                "history": [],
                "created_at": time.time()
            }
            self._save_to_disk()
        return self._quotas[clean_ip]

    def sync_client_state(
        self,
        ip: str,
        client_free_used: Optional[int] = None,
        client_paid_tier: Optional[int] = None,
        client_paid_credits: Optional[int] = None,
        client_tx_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Đồng bộ hóa bất biến (Monotonic Sync) giữa Client và Server:
        Đảm bảo sau mỗi lần trang web được cập nhật / redeploy container:
        1. Số lượt miễn phí đã dùng (free_used) KHÔNG BAO GIỜ bị quay về 0.
        2. Số lượt gói trả phí hợp lệ (paid_credits kèm mã giao dịch TIMO-...) KHÔNG BAO GIỜ bị mất.
        """
        rec = self.get_record(ip)
        changed = False

        # 1. Bảo toàn tuyệt đối số lượt miễn phí đã dùng (chỉ tăng, không bao giờ giảm về cũ)
        if client_free_used is not None:
            try:
                cfu = max(0, min(2, int(client_free_used)))
                if cfu > rec.get("free_used", 0):
                    rec["free_used"] = cfu
                    changed = True
            except Exception:
                pass

        # 2. Khôi phục hạn mức trả phí nếu container vừa cập nhật mới và client còn lượt hợp lệ
        if client_paid_credits is not None and client_paid_tier is not None and client_tx_id:
            try:
                cpc = max(0, min(20, int(client_paid_credits)))
                cpt = int(client_paid_tier)
                ctx = str(client_tx_id).strip()
                exhausted_map = self._quotas.get("_exhausted_tx", {})

                if (
                    cpc > 0
                    and cpt in (1, 2, 3)
                    and ctx.startswith("TIMO-")
                    and len(ctx) >= 12
                    and ctx not in exhausted_map
                    and rec.get("paid_credits", 0) == 0
                    and rec.get("last_tx_id", "") != ctx
                ):
                    rec["paid_tier"] = cpt
                    rec["paid_credits"] = cpc
                    rec["last_tx_id"] = ctx
                    if cpt == 3 and not rec.get("paid_expires_at"):
                        rec["paid_expires_at"] = int((time.time() + 30 * 86400) * 1000)
                    changed = True
            except Exception:
                pass

        if changed:
            self._save_to_disk()

        return rec

    def _get_tier_label(self, tier: int) -> str:
        if tier == 3:
            return "Gói 3 (50.000đ - 20 lượt / 30 ngày)"
        if tier == 2:
            return "Gói 2 (10.000đ - Chuyên gia)"
        if tier == 1:
            return "Gói 1 (3.000đ - Tiêu chuẩn)"
        return "Bản Miễn Phí (Free)"

    def get_quota_status(self, ip: str) -> Dict[str, Any]:
        """Tính toán trạng thái hạn mức và quyền truy cập hiện tại của IP"""
        rec = self.get_record(ip)
        free_used = rec.get("free_used", 0)
        paid_tier = rec.get("paid_tier", 0)
        paid_credits = rec.get("paid_credits", 0)
        paid_expires_at = rec.get("paid_expires_at", 0)

        # Kiểm tra thời hạn 30 ngày của Gói 3 nếu có
        now_ms = int(time.time() * 1000)
        if paid_credits > 0 and paid_expires_at and now_ms > paid_expires_at:
            paid_credits = 0
            paid_tier = 0
            rec["paid_credits"] = 0
            rec["paid_tier"] = 0
            self._save_to_disk()

        last_tx_id = rec.get("last_tx_id", "")
        free_remaining = max(0, 2 - free_used)
        can_scan = (free_remaining > 0) or (paid_credits > 0)
        active_tier = paid_tier if paid_credits > 0 else 0

        return {
            "ip": rec.get("ip", ip),
            "free_used": free_used,
            "free_remaining": free_remaining,
            "paid_tier": paid_tier,
            "paid_credits": paid_credits,
            "paid_expires_at": paid_expires_at,
            "last_tx_id": last_tx_id,
            "active_tier": active_tier,
            "can_scan": can_scan,
            "tier_name": self._get_tier_label(active_tier)
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
        paid_expires_at = rec.get("paid_expires_at", 0)
        free_used = rec.get("free_used", 0)

        now_ms = int(time.time() * 1000)
        if paid_credits > 0 and paid_expires_at and now_ms > paid_expires_at:
            paid_credits = 0
            paid_tier = 0
            rec["paid_credits"] = 0
            rec["paid_tier"] = 0
            self._save_to_disk()

        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC+7", time.gmtime(time.time() + 7 * 3600))

        # 1. Trường hợp có lượt trả phí (Gói 1, Gói 2 hoặc Gói 3)
        if paid_credits > 0:
            tier_used = paid_tier
            rec["paid_credits"] = paid_credits - 1
            if rec["paid_credits"] <= 0:
                rec["paid_tier"] = 0
                last_tx = rec.get("last_tx_id", "")
                if last_tx:
                    self._quotas.setdefault("_exhausted_tx", {})[last_tx] = now_str
            rec.setdefault("history", []).append({
                "action": "CONSUME_SCAN",
                "type": "PAID",
                "tier": tier_used,
                "time": now_str
            })
            self._save_to_disk()
            print(f"[QuotaManager] Đã trừ 1 lượt trả phí (Gói {tier_used}) của IP: {ip}. Còn lại: {rec['paid_credits']}")
            quota_status = self.get_quota_status(ip)
            quota_status["active_tier"] = tier_used
            quota_status["tier_name"] = self._get_tier_label(tier_used)
            return {
                "allowed": True,
                "tier_used": tier_used,
                "type": "PAID",
                "credits_remaining": rec["paid_credits"],
                "quota": quota_status
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
        Cấp lượt sử dụng cho gói trả phí sau khi ĐÃ XÁC THỰC THÀNH CÔNG THANH TOÁN:
        - Gói 3 (50.000đ): Cung cấp 20 lượt truy cập cao cấp (gấp 10 lần gói 2) trong 30 ngày.
        - Gói 2 (10.000đ): Cung cấp 2 lượt truy cập cao cấp.
        - Gói 1 (3.000đ): Cung cấp 1 lượt kiểm tra chỉ số.
        """
        rec = self.get_record(ip)
        rec["paid_tier"] = package_id
        if package_id == 3:
            rec["paid_credits"] = 20
            rec["paid_expires_at"] = int((time.time() + 30 * 86400) * 1000)
        elif package_id == 2:
            rec["paid_credits"] = 2
            rec["paid_expires_at"] = 0
        else:
            rec["paid_credits"] = 1
            rec["paid_expires_at"] = 0
        if tx_id:
            rec["last_tx_id"] = tx_id
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
