"""
data.py — JSON-based storage for the Timetable Manager.

Storage structure (data.json):
{
  "timetable": {
    "Monday": [{"time": "09:00", "subject": "Math", "location": "Room 101", "color": "cyan"}, ...],
    ...
  },
  "tasks": {
    "2025-01-20": [{"id": 1, "title": "...", "desc": "...", "priority": "high", "done": false, "time": "14:00"}, ...],
    ...
  },
  "events": {
    "2025-01": [{"id": 1, "title": "...", "date": "2025-01-20", "time": "10:00", "desc": "...", "color": "green"}, ...],
    ...
  },
  "notes": {
    "2025-01-20": "Some note text..."
  }
}
"""

import json
import os
from datetime import datetime, date

DATA_FILE = "data.json"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

COLORS = ["cyan", "green", "yellow", "magenta", "red", "blue", "white"]

PRIORITY_COLORS = {
    "high":   "red",
    "medium": "yellow",
    "low":    "green",
}

# ── Load / Save ────────────────────────────────────────────────────────────────

def _default() -> dict:
    return {
        "timetable": {day: [] for day in DAYS},
        "tasks": {},
        "events": {},
        "notes": {},
    }


def load() -> dict:
    if not os.path.exists(DATA_FILE):
        return _default()
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        # Ensure all keys exist (forward compatibility)
        for key in _default():
            data.setdefault(key, _default()[key])
        for day in DAYS:
            data["timetable"].setdefault(day, [])
        return data
    except (json.JSONDecodeError, KeyError):
        return _default()


def save(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── ID helpers ────────────────────────────────────────────────────────────────

def _next_id(items: list) -> int:
    return max((i.get("id", 0) for i in items), default=0) + 1


# ── Timetable ─────────────────────────────────────────────────────────────────

def get_timetable(day: str) -> list:
    data = load()
    slots = data["timetable"].get(day, [])
    return sorted(slots, key=lambda x: x.get("time", "00:00"))


def add_slot(day: str, time: str, subject: str, location: str, color: str) -> None:
    data = load()
    data["timetable"][day].append({
        "id":       _next_id(data["timetable"][day]),
        "time":     time,
        "subject":  subject,
        "location": location,
        "color":    color,
    })
    save(data)


def delete_slot(day: str, slot_id: int) -> bool:
    data = load()
    slots = data["timetable"][day]
    new   = [s for s in slots if s["id"] != slot_id]
    if len(new) == len(slots):
        return False
    data["timetable"][day] = new
    save(data)
    return True


def edit_slot(day: str, slot_id: int, **kwargs) -> bool:
    data = load()
    for slot in data["timetable"][day]:
        if slot["id"] == slot_id:
            slot.update(kwargs)
            save(data)
            return True
    return False


# ── Tasks ─────────────────────────────────────────────────────────────────────

def get_tasks(date_str: str) -> list:
    data = load()
    tasks = data["tasks"].get(date_str, [])
    return sorted(tasks, key=lambda x: (x.get("done", False), x.get("time", "00:00")))


def add_task(date_str: str, title: str, desc: str, priority: str, time: str) -> None:
    data = load()
    data["tasks"].setdefault(date_str, [])
    data["tasks"][date_str].append({
        "id":       _next_id(data["tasks"][date_str]),
        "title":    title,
        "desc":     desc,
        "priority": priority,
        "time":     time,
        "done":     False,
    })
    save(data)


def toggle_task(date_str: str, task_id: int) -> bool:
    data = load()
    for task in data["tasks"].get(date_str, []):
        if task["id"] == task_id:
            task["done"] = not task["done"]
            save(data)
            return True
    return False


def delete_task(date_str: str, task_id: int) -> bool:
    data = load()
    tasks = data["tasks"].get(date_str, [])
    new   = [t for t in tasks if t["id"] != task_id]
    if len(new) == len(tasks):
        return False
    data["tasks"][date_str] = new
    save(data)
    return True


def get_week_tasks(week_dates: list) -> dict:
    """Return {date_str: [tasks]} for a list of date strings."""
    return {d: get_tasks(d) for d in week_dates}


# ── Events (monthly) ──────────────────────────────────────────────────────────

def get_month_events(year_month: str) -> list:
    """year_month format: '2025-01'"""
    data = load()
    return sorted(
        data["events"].get(year_month, []),
        key=lambda x: (x.get("date", ""), x.get("time", "00:00")),
    )


def add_event(year_month: str, title: str, date_str: str, time: str, desc: str, color: str) -> None:
    data = load()
    data["events"].setdefault(year_month, [])
    data["events"][year_month].append({
        "id":    _next_id(data["events"][year_month]),
        "title": title,
        "date":  date_str,
        "time":  time,
        "desc":  desc,
        "color": color,
    })
    save(data)


def delete_event(year_month: str, event_id: int) -> bool:
    data = load()
    events = data["events"].get(year_month, [])
    new    = [e for e in events if e["id"] != event_id]
    if len(new) == len(events):
        return False
    data["events"][year_month] = new
    save(data)
    return True


# ── Notes ─────────────────────────────────────────────────────────────────────

def get_note(date_str: str) -> str:
    return load()["notes"].get(date_str, "")


def save_note(date_str: str, text: str) -> None:
    data = load()
    data["notes"][date_str] = text
    save(data)
