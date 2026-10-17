import time
import threading
from typing import Any, Optional
from .models import Job


class ResultStore:
    def __init__(self) -> None:
        self._results = {}
        self._jobs    = {}
        self._lock    = threading.Lock()

    def save_job(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def save_result(self, job_id: str, result: Any,
                    error: Optional[str]) -> None:
        with self._lock:
            self._results[job_id] = {
                "result":   result,
                "error":    error,
                "saved_at": time.monotonic(),
            }

    def get_result(self, job_id: str) -> Optional[dict]:
        with self._lock:
            return self._results.get(job_id)

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def all_results(self) -> dict:
        with self._lock:
            return dict(self._results)

    def count(self) -> int:
        with self._lock:
            return len(self._results)

    def clear_older_than(self, seconds: float) -> int:
        now     = time.monotonic()
        removed = 0
        with self._lock:
            for job_id, data in list(self._results.items()):
                if now - data["saved_at"] > seconds:
                    del self._results[job_id]
                    removed += 1
        return removed
