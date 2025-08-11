#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS_JSON = ROOT / "tasks" / "tasks.json"
TASKS_DIR = ROOT / "tasks"
DOCS_DIR = ROOT / "docs"

ALLOWED_STATUS = {"pending", "in-progress", "review", "done", "deferred", "cancelled"}


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}")
    sys.exit(1)


def load_tasks() -> dict:
    if not TASKS_JSON.exists():
        fail(f"Missing tasks file: {TASKS_JSON}")
    try:
        return json.loads(TASKS_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Invalid JSON in {TASKS_JSON}: {e}")


def validate_ids_unique(tasks: list) -> None:
    seen = set()
    for t in tasks:
        tid = t.get("id")
        if not tid:
            fail("Task without id")
        if tid in seen:
            fail(f"Duplicate task id: {tid}")
        seen.add(tid)
        # Validate subtasks
        st_seen = set()
        for st in t.get("subtasks", []):
            sid = st.get("id")
            if not sid:
                fail(f"Task {tid} has subtask without id")
            if sid in st_seen:
                fail(f"Task {tid} has duplicate subtask id: {sid}")
            if not re.match(rf"^{re.escape(tid)}\.\d+$", sid):
                fail(f"Subtask id {sid} must start with '{tid}.' and a number")
            st_seen.add(sid)


def validate_links_and_files(tasks: list) -> None:
    for t in tasks:
        tid = t["id"]
        # Check docs links exist
        for rel in t.get("links", []):
            p = ROOT / rel
            if not p.exists():
                fail(f"Task {tid} link missing: {rel}")
        # Check task markdown exists
        md_candidates = list(TASKS_DIR.glob(f"{tid}-*.md"))
        if not md_candidates:
            fail(f"Task {tid} markdown file not found in tasks/ (pattern {tid}-*.md)")
        # Validate subtask statuses
        for st in t.get("subtasks", []):
            status = st.get("status")
            if status not in ALLOWED_STATUS:
                fail(f"Task {tid} subtask {st.get('id')} has invalid status: {status}")


def main() -> None:
    data = load_tasks()
    if "tasks" not in data or not isinstance(data["tasks"], list):
        fail("tasks.json must contain 'tasks' array")
    tasks = data["tasks"]
    validate_ids_unique(tasks)
    validate_links_and_files(tasks)
    print("[OK] tasks/ structure and links validated")


if __name__ == "__main__":
    main()
