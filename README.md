# Engineering Assignment

Read this before opening the notebook.

---

## What this is

A job processing pipeline. The system accepts work, queues it by priority, dispatches it to a pool of workers, and stores results. It is the kind of system that underpins anything that needs to process work reliably at scale.

The codebase has problems and missing pieces. Your job is to find them, fix them, and extend the system.

---

## Structure

```
project/
├── README.md
├── assignment.ipynb
└── src/
    ├── models.py         do not modify
    ├── benchmark.py      do not modify
    ├── job_queue.py      Phase 1 — fix this
    ├── worker_pool.py    Phase 1 — fix this
    ├── result_store.py   Phase 1 — fix this
    └── dispatcher.py     Phase 1 — fix this
```

Phase 3 — you create new src files for the features you add.

---

## The three phases

**Phase 1** — four src files are broken. They run without errors in simple cases but fail under specific conditions. Find what is wrong, fix it.

**Phase 2** — the system is correct but has three distinct failure modes under real conditions. Each is measured in the notebook. You write code in the notebook to fix each one. You do not modify src files in this phase.

**Phase 3** — add two features. Create new src files. Show them working.

Each phase is evaluated independently. Doing two phases well is better than attempting three poorly.

---

## Rules

- `models.py` and `benchmark.py` — do not modify under any circumstances
- Phase 1 — modify only the four broken src files
- Phase 2 — no src modifications, all code in the notebook implementation cells
- Phase 3 — create new src files, modify existing ones only if absolutely necessary
- Do not add external dependencies beyond `psutil` and standard library

---

## Setup

```bash
pip install psutil
```

Python 3.10 or higher. Works on Mac, Linux, Windows.

---

## Submitting

Run all cells top to bottom. Make sure all outputs are visible. Run the final cell — it generates `result.csv`. Zip the entire project folder and submit via the link provided.

---

## Notes cells

There is a notes cell after each phase. Write what you found, what you changed, and why. These are read as part of the evaluation.
