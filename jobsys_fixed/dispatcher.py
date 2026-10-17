import time
import threading
import logging
from typing import Callable, Optional

from .models import Job, JobStatus
from .job_queue import JobQueue
from .worker_pool import WorkerPool
from .result_store import ResultStore

log = logging.getLogger(__name__)


def _process(job: Job) -> dict:
    total = sum(i * i for i in range(500))
    return {"processed": job.payload, "result": total}


class Dispatcher:
    def __init__(self,
                 process_fn: Callable[[Job], object] = _process,
                 num_workers: int = 6) -> None:
        self._store      = ResultStore()
        self._queue      = JobQueue()
        self._process_fn = process_fn
        self._running    = False
        self._thread     = None
        self._pool       = WorkerPool(
            on_done=lambda jid, res, err: self._on_done(jid, res, err),
            num_workers=num_workers
        )

    def _on_done(self, job_id: str, result: object,
                 error: Optional[str]) -> None:
        self._store.save_result(job_id, result, error)

    def start(self) -> None:
        self._running = True
        self._pool.start()
        self._thread  = threading.Thread(
            target=self._dispatch_loop,
            daemon=True,
            name="dispatcher"
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
        self._pool.stop()

    def submit(self, job_id: str, payload: dict,
               priority: int,
               ttl_seconds: Optional[float] = None) -> str:
        job = Job(
            job_id=job_id,
            payload=payload,
            priority=priority,
            ttl_seconds=ttl_seconds,
        )
        self._store.save_job(job)
        self._queue.push(job)
        return job_id

    def get_result(self, job_id: str) -> Optional[dict]:
        return self._store.get_result(job_id)

    def get_status(self, job_id: str) -> Optional[JobStatus]:
        job = self._store.get_job(job_id)
        return job.status if job else None

    def result_count(self) -> int:
        return self._store.count()

    def _dispatch_loop(self) -> None:
        while self._running:
            job = self._queue.pop()
            if job is None:
                time.sleep(0.001)
                continue
            dispatched = self._pool.submit(job, self._process_fn)
            if not dispatched:
                self._queue.push(job)
                time.sleep(0.001)
