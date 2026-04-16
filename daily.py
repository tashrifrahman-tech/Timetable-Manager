"""
daily.py — Day-to-day task manager (Tab 2).

Features:
  • Add / complete / delete tasks for any date
  • Each task has: title, description, priority (high/medium/low), time
  • Shows today's timetable alongside tasks
  • Daily notes section
  • Navigate to prev/next day
"""

from datetime import date, timedelta
from rich.console import Console
from rich.table   import Table
from rich.columns import Columns
from rich.panel   import Panel
from rich.text    import Text
from rich         import box

import data
import utils

console = Console()


# ── Views ──────────────────────────────────────────────────────────────────────

def view_day(date_str: str):
    """Show timetable + tasks + note for a single day."""
    day_name = utils.day_name(date_str)
    utils.header(
        f"📅  {utils.friendly_date(date_str)}",
        "Daily Overview", "green",
    )

    # ── Timetable panel ──
    slots = data.get_timetable(day_name)
    tt_lines = Text()
    if slots:
        for s in slots:
            color = s.get("color", "cyan")
            tt_lines.append(f"  {s['time']}  ", style="white")
            tt_lines.append(f"{s['subject']}", style=f"bold {color}")
            if s.get("location"):
                tt_lines.append(f"  ({s['location']})", style="dim")
            tt_lines.append("\n")
    else:
        tt_lines.append("  No classes scheduled.\n", style="dim")

    tt_panel = Panel(tt_lines, title="[bold cyan]📋 Timetable[/]",
                     border_style="cyan", expand=True)

    # ── Tasks panel ──
    tasks = data.get_tasks(date_str)
    task_lines = Text()
    if tasks:
        for t in tasks:
            done_mark = "[green]✓[/green]" if t["done"] else "[dim]○[/dim]"
            pcolor    = utils.PRIORITY_STYLE.get(t["priority"], "white")
            strike    = "strike " if t["done"] else ""
            task_lines.append(f"  [{done_mark}]  ", style="white")
            task_lines.append(f"[{t['id']}]  ", style="dim")
            if t.get("time"):
                task_lines.append(f"{t['time']}  ", style="white")
            task_lines.append(f"{t['title']}\n", style=f"{strike}{pcolor}")
    else:
        task_lines.append("  No tasks for today.\n", style="dim")

    task_panel = Panel(task_lines, title="[bold green]✅ Tasks[/]",
                       border_style="green", expand=True)

    console.print(Columns([tt_panel, task_panel], equal=True, expand=True))

    # ── Note ──
    note = data.get_note(date_str)
    if note:
        console.print(Panel(f"  {note}", title="[bold yellow]📝 Note[/]",
                            border_style="yellow", expand=True))


# ── Actions ────────────────────────────────────────────────────────────────────

def add_task(date_str: str):
    utils.header("➕  Add Task", f"For {utils.friendly_date(date_str)}", "green")

    title = utils.prompt("Task title")
    if not title:
        utils.error("Title cannot be empty.")
        utils.pause()
        return

    desc     = utils.prompt("Description (optional)")
    time_val = utils.ask_time("Time (HH:MM, optional)", "")
    priority = utils.pick_priority()

    data.add_task(date_str, title, desc, priority, time_val)
    utils.success(f"Task '{title}' added.")
    utils.pause()


def toggle_task(date_str: str):
    view_day(date_str)
    tasks = data.get_tasks(date_str)
    if not tasks:
        utils.pause()
        return

    raw = utils.prompt("Enter task ID to mark done/undone")
    try:
        task_id = int(raw)
    except ValueError:
        utils.error("Invalid ID.")
        utils.pause()
        return

    if data.toggle_task(date_str, task_id):
        utils.success("Task toggled.")
    else:
        utils.error("Task not found.")
    utils.pause()


def delete_task(date_str: str):
    view_day(date_str)
    tasks = data.get_tasks(date_str)
    if not tasks:
        utils.pause()
        return

    raw = utils.prompt("Enter task ID to delete")
    try:
        task_id = int(raw)
    except ValueError:
        utils.error("Invalid ID.")
        utils.pause()
        return

    if data.delete_task(date_str, task_id):
        utils.success("Task deleted.")
    else:
        utils.error("Task not found.")
    utils.pause()


def edit_note(date_str: str):
    utils.header("📝  Daily Note", f"For {utils.friendly_date(date_str)}", "yellow")
    existing = data.get_note(date_str)
    if existing:
        console.print(f"\n  [dim]Current note:[/] {existing}")

    text = utils.prompt("Enter note (leave blank to clear)")
    data.save_note(date_str, text)
    utils.success("Note saved.")
    utils.pause()


# ── Menu ───────────────────────────────────────────────────────────────────────

def menu():
    current = utils.today_str()

    while True:
        view_day(current)
        console.print()
        console.print(f"  [dim]Viewing:[/] [bold white]{utils.friendly_date(current)}[/]")
        console.print()
        console.print("  [bold cyan]1.[/] ➕  Add Task")
        console.print("  [bold cyan]2.[/] ✅  Mark Task Done / Undone")
        console.print("  [bold cyan]3.[/] 🗑️   Delete Task")
        console.print("  [bold cyan]4.[/] 📝  Edit Daily Note")
        console.print("  [bold cyan]5.[/] ◀   Previous Day")
        console.print("  [bold cyan]6.[/] ▶   Next Day")
        console.print("  [bold cyan]7.[/] 📅  Jump to Date")
        console.print("  [bold cyan]8.[/] 🏠  Go to Today")
        console.print("  [bold cyan]0.[/] ← Back to Main Menu")

        choice = utils.prompt("Choice")

        if   choice == "1": add_task(current)
        elif choice == "2": toggle_task(current)
        elif choice == "3": delete_task(current)
        elif choice == "4": edit_note(current)
        elif choice == "5":
            from datetime import datetime, timedelta
            d = datetime.strptime(current, "%Y-%m-%d").date()
            current = (d - timedelta(days=1)).isoformat()
        elif choice == "6":
            from datetime import datetime, timedelta
            d = datetime.strptime(current, "%Y-%m-%d").date()
            current = (d + timedelta(days=1)).isoformat()
        elif choice == "7":
            current = utils.ask_date("Jump to date (YYYY-MM-DD)", current)
        elif choice == "8":
            current = utils.today_str()
        elif choice == "0":
            break
        else:
            utils.error("Invalid choice.")
