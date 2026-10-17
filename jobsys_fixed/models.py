from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time


class JobStatus(Enum):
    PENDING   = "PENDING"
    RUNNING   = "RUNNING"
    DONE      = "DONE"
    FAILED    = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED   = "EXPIRED"


@dataclass
class Job:
    job_id:      str
    payload:     dict
    priority:    int
    ttl_seconds: Optional[float] = None
    status:      JobStatus       = JobStatus.PENDING
    result:      Optional[Any]   = None
    error:       Optional[str]   = None
    created_at:  float           = field(default_factory=time.monotonic)
    started_at:  Optional[float] = None
    finished_at: Optional[float] = None

    def age_seconds(self) -> float:
        return time.monotonic() - self.created_at

    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        return self.age_seconds() > self.ttl_seconds
