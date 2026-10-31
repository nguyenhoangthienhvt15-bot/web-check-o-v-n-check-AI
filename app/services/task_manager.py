import time
import asyncio
import traceback
from typing import Dict, Any, Optional

class AsyncTaskManager:
    """
    HỆ THỐNG QUẢN LÝ HÀNG ĐỢI XỬ LÝ NGẦM BẤT ĐỒNG BỘ (ASYNC TASK QUEUE)
    ------------------------------------------------------------------
    Giúp xử lý các tài liệu quy mô lớn (luận án 100 - 300 trang) mà không bị HTTP Timeout,
    đồng thời truyền tải phần trăm tiến trình thời gian thực cho thanh chạy sóng biển RGB.
    """
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, task_id: str, filename: str) -> Dict[str, Any]:
        task_info = {
            "task_id": task_id,
            "filename": filename,
            "status": "QUEUED",
            "progress_percent": 5,
            "current_stage": "Đang tiếp nhận tệp vào hàng đợi thẩm định pháp y...",
            "created_at": time.time(),
            "updated_at": time.time(),
            "result": None,
            "error": None
        }
        self._tasks[task_id] = task_info
        self._prune_old_tasks()
        return task_info

    def update_progress(
        self,
        task_id: str,
        stage: str,
        percent: int,
        status: str = "PROCESSING",
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = status
            self._tasks[task_id]["current_stage"] = stage
            self._tasks[task_id]["progress_percent"] = max(0, min(100, percent))
            self._tasks[task_id]["updated_at"] = time.time()
            if result is not None:
                self._tasks[task_id]["result"] = result
            if error is not None:
                self._tasks[task_id]["error"] = error

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def _prune_old_tasks(self):
        """Tự động dọn dẹp các tác vụ cũ quá 3 giờ để tối ưu RAM"""
        now = time.time()
        expired = [tid for tid, t in self._tasks.items() if now - t.get("created_at", 0) > 10800]
        for tid in expired:
            del self._tasks[tid]

# Singleton instance
async_task_manager = AsyncTaskManager()
