import heapq
import threading
from typing import Optional
from .models import Job


class JobQueue:
    def __init__(self) -> None:
        self._heap  = []
        self._lock  = threading.Lock()
        self._count = 0

    def push(self, job: Job) -> None:
        with self._lock:
            heapq.heappush(self._heap, (job.priority, self._count, job))
            self._count += 1

    def pop(self) -> Optional[Job]:
        with self._lock:
            if not self._heap:
                return None
            _, _, job = heapq.heappop(self._heap)
            return job

    def size(self) -> int:
        with self._lock:
            return len(self._heap)

    def empty(self) -> bool:
        with self._lock:
            return len(self._heap) == 0
