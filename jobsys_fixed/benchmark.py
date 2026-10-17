"""
Do not modify this file.
"""

import time
import threading
import statistics
import uuid
import psutil
import os
from typing import Optional


def run_benchmark(dispatcher, duration_seconds: int = 20,
                  submit_rate_per_sec: int = 500) -> dict:
    completed    = []
    failed_ids   = []
    submit_times = {}
    latencies    = []
    cpu_samples  = []
    lock         = threading.Lock()
    stop_event   = threading.Event()

    original_on_done = dispatcher._on_done

    def measuring_on_done(job_id, result, error):
        finish = time.monotonic()
        with lock:
            start = submit_times.get(job_id)
            if start:
                latencies.append((finish - start) * 1000)
            if error:
                failed_ids.append(job_id)
            else:
                completed.append(job_id)
        original_on_done(job_id, result, error)

    dispatcher._on_done = measuring_on_done

    proc = psutil.Process(os.getpid())

    def sample_cpu():
        while not stop_event.is_set():
            cpu_samples.append(proc.cpu_percent(interval=0.1))

    cpu_thread = threading.Thread(target=sample_cpu, daemon=True)
    cpu_thread.start()

    dispatcher.start()
    start_time     = time.monotonic()
    interval       = 1.0 / submit_rate_per_sec
    jobs_submitted = 0

    while time.monotonic() - start_time < duration_seconds:
        job_id  = str(uuid.uuid4())[:8]
        payload = {"job_id": job_id, "action": "process",
                   "value": jobs_submitted % 100}
        priority = (jobs_submitted % 10) + 1
        with lock:
            submit_times[job_id] = time.monotonic()
        try:
            dispatcher.submit(job_id=job_id, payload=payload,
                              priority=priority)
            jobs_submitted += 1
        except Exception:
            pass
        time.sleep(interval)

    drain_start = time.monotonic()
    while time.monotonic() - drain_start < 5.0:
        with lock:
            if len(completed) + len(failed_ids) >= jobs_submitted:
                break
        time.sleep(0.05)

    stop_event.set()
    dispatcher.stop()
    elapsed = time.monotonic() - start_time

    dispatcher._on_done = original_on_done

    jobs_done  = len(completed)
    throughput = round(jobs_done / elapsed, 1)

    if latencies:
        s    = sorted(latencies)
        p50  = round(statistics.median(s), 2)
        p99  = round(s[max(0, int(len(s) * 0.99) - 1)], 2)
    else:
        p50 = p99 = 0.0

    cpu_usage = round(statistics.mean(cpu_samples), 1) if cpu_samples else 0.0
    cpu_idle  = round(100 - cpu_usage, 1)

    return {
        "duration_sec":   round(elapsed, 1),
        "jobs_submitted": jobs_submitted,
        "jobs_completed": jobs_done,
        "jobs_failed":    len(failed_ids),
        "throughput":     throughput,
        "p50_ms":         p50,
        "p99_ms":         p99,
        "cpu_usage_pct":  cpu_usage,
        "cpu_idle_pct":   cpu_idle,
    }


def print_benchmark(label: str, r: dict) -> None:
    print(f"\n  {label}")
    print(f"  {'─'*38}")
    print(f"  throughput     : {r['throughput']} jobs/sec")
    print(f"  p50 latency    : {r['p50_ms']} ms")
    print(f"  p99 latency    : {r['p99_ms']} ms")
    print(f"  cpu idle       : {r['cpu_idle_pct']}%")
    print(f"  completed      : {r['jobs_completed']} / {r['jobs_submitted']}")
