import threading
import time
import logging
from typing import Callable, Optional
from .models import Job, JobStatus

log = logging.getLogger(__name__)


class WorkerPool:
    def __init__(self,
                 on_done: Callable[[str, object, Optional[str]], None],
                 num_workers: int = 6) -> None:
        self._on_done     = on_done
        self._num_workers = num_workers
        self._semaphore   = threading.Semaphore(num_workers)
        self._running     = False
        self._threads     = []

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False
        for t in self._threads:
            t.join(timeout=2.0)

    def submit(self, job: Job,
               process_fn: Callable[[Job], object]) -> bool:
        acquired = self._semaphore.acquire(blocking=False)
        if not acquired:
            return False
        t = threading.Thread(
            target=self._run_job,
            args=(job, process_fn),
            daemon=True
        )
        self._threads.append(t)
        t.start()
        return True

    def _run_job(self, job: Job,
                 process_fn: Callable[[Job], object]) -> None:
        try:
            job.status      = JobStatus.RUNNING
            job.started_at  = time.monotonic()
            result          = process_fn(job)
            job.status      = JobStatus.DONE
            job.finished_at = time.monotonic()
            self._semaphore.release()
            self._on_done(job.job_id, result, None)
        except Exception as e:
            job.status      = JobStatus.FAILED
            job.error       = str(e)
            job.finished_at = time.monotonic()
            self._semaphore.release()
            self._on_done(job.job_id, None, str(e))

    def available_slots(self) -> int:
        return self._semaphore._value
