"""
weekly.py — Weekly overview and task manager (Tab 3).

Features:
  • Full week at a glance: timetable row + tasks per day
  • Task completion progress bar per day
  • Navigate prev/next weeks
  • Add tasks for any day in the week
"""

from datetime import datetime, timedelta
from rich.console import Console
from rich.table   import Table
from rich.text    import Text
from rich         import box

import data
import utils

console = Console()

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ── Progress bar ───────────────────────────────────────────────────────────────

def _progress(done: int, total: int, width: int = 10) -> str:
    if total == 0:
        return "[dim]" + "─" * width + "[/dim]"
    filled = round(done / total * width)
    bar    = "█" * filled + "░" * (width - filled)
    color  = "green" if done == total else "yellow" if done > 0 else "dim"
    return f"[{color}]{bar}[/{color}]  [dim]{done}/{total}[/dim]"


# ── View ───────────────────────────────────────────────────────────────────────

def view_week(week_offset: int = 0):
    dates    = utils.week_dates(week_offset)
    day_names = [utils.day_name(d) for d in dates]

    week_start = datetime.strptime(dates[0], "%Y-%m-%d").strftime("%d %b")
    week_end   = datetime.strptime(dates[6], "%Y-%m-%d").strftime("%d %b %Y")
    utils.header(
        f"📆  Week of {week_start} – {week_end}",
        "Weekly Overview", "blue",
    )

    today = utils.today_str()

    # ── Summary table ──
    table = Table(box=box.ROUNDED, border_style="blue", expand=True, show_lines=True)
    table.add_column("",     style="bold", width=5)
    for i, (abbr, d) in enumerate(zip(DAY_ABBR, dates)):
        is_today = d == today
        date_num = datetime.strptime(d, "%Y-%m-%d").day
        header_txt = f"[bold {'white' if is_today else 'cyan'}]{abbr} {date_num:02d}{'  ★' if is_today else ''}[/]"
        table.add_column(header_txt, min_width=18)

    # Row 1: Timetable slots
    tt_row = ["[bold dim]TT[/]"]
    for day_name_str in day_names:
        slots = data.get_timetable(day_name_str)
        if slots:
            cell = Text()
            for s in slots[:3]:              # show max 3
                color = s.get("color", "cyan")
                cell.append(f"• {s['time']} ", style="dim")
                cell.append(f"{s['subject'][:12]}\n", style=f"bold {color}")
            if len(slots) > 3:
                cell.append(f"  +{len(slots)-3} more\n", style="dim")
            tt_row.append(cell)
        else:
            tt_row.append(Text("—", style="dim"))
    table.add_row(*tt_row)

    # Row 2: Tasks
    task_row = ["[bold dim]Tasks[/]"]
    for d in dates:
        tasks = data.get_tasks(d)
        if tasks:
            cell = Text()
            for t in tasks[:3]:
                done_icon = "✓ " if t["done"] else "○ "
                pcolor    = {"high": "red", "medium": "yellow", "low": "green"}.get(t["priority"], "white")
                style     = f"strike dim" if t["done"] else f"bold {pcolor}"
                cell.append(f"{done_icon}{t['title'][:14]}\n", style=style)
            if len(tasks) > 3:
                cell.append(f"  +{len(tasks)-3} more\n", style="dim")
            task_row.append(cell)
        else:
            task_row.append(Text("—", style="dim"))
    table.add_row(*task_row)

    # Row 3: Progress
    prog_row = ["[bold dim]Progress[/]"]
    for d in dates:
        tasks = data.get_tasks(d)
        done  = sum(1 for t in tasks if t["done"])
        prog_row.append(_progress(done, len(tasks)))
    table.add_row(*prog_row)

    console.print(table)

    # ── Weekly summary stats ──
    all_tasks = [t for d in dates for t in data.get_tasks(d)]
    total = len(all_tasks)
    done  = sum(1 for t in all_tasks if t["done"])
    high  = sum(1 for t in all_tasks if t["priority"] == "high" and not t["done"])

    console.print(
        f"\n  [dim]Week total:[/] [bold]{total}[/] tasks  |  "
        f"[green]✓ {done} done[/]  |  "
        f"[yellow]◉ {total - done} pending[/]  |  "
        f"[red]⚑ {high} high-priority pending[/]"
    )
    return dates


# ── Actions ────────────────────────────────────────────────────────────────────

def add_task_for_day(dates: list):
    """Pick a day from the current week and add a task."""
    abbrs = [f"{DAY_ABBR[i]} ({dates[i]})" for i in range(7)]
    idx   = utils.pick_from(abbrs, "Add task for which day")
    if idx is None:
        return

    date_str = dates[idx]
    title    = utils.prompt("Task title")
    if not title:
        utils.error("Title cannot be empty.")
        utils.pause()
        return
    desc     = utils.prompt("Description (optional)")
    time_val = utils.ask_time("Time (HH:MM, optional)", "")
    priority = utils.pick_priority()

    data.add_task(date_str, title, desc, priority, time_val)
    utils.success(f"Task added to {utils.friendly_date(date_str)}.")
    utils.pause()


def toggle_task_for_day(dates: list):
    abbrs = [f"{DAY_ABBR[i]} ({dates[i]})" for i in range(7)]
    idx   = utils.pick_from(abbrs, "Toggle task for which day")
    if idx is None:
        return
    date_str = dates[idx]
    tasks    = data.get_tasks(date_str)
    if not tasks:
        utils.info("No tasks on that day.")
        utils.pause()
        return

    console.print()
    for t in tasks:
        icon   = "[green]✓[/]" if t["done"] else "[dim]○[/]"
        pcolor = {"high": "red", "medium": "yellow", "low": "green"}.get(t["priority"], "white")
        console.print(f"  {icon} [{t['id']}] [{pcolor}]{t['title']}[/{pcolor}]")

    raw = utils.prompt("Task ID")
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


# ── Menu ───────────────────────────────────────────────────────────────────────

def menu():
    offset = 0

    while True:
        dates = view_week(offset)
        console.print()
        console.print("  [bold cyan]1.[/] ➕  Add Task to a Day")
        console.print("  [bold cyan]2.[/] ✅  Mark Task Done / Undone")
        console.print("  [bold cyan]3.[/] ◀   Previous Week")
        console.print("  [bold cyan]4.[/] ▶   Next Week")
        console.print("  [bold cyan]5.[/] 🏠  This Week")
        console.print("  [bold cyan]0.[/] ← Back to Main Menu")

        choice = utils.prompt("Choice")

        if   choice == "1": add_task_for_day(dates)
        elif choice == "2": toggle_task_for_day(dates)
        elif choice == "3": offset -= 1
        elif choice == "4": offset += 1
        elif choice == "5": offset  = 0
        elif choice == "0": break
        else: utils.error("Invalid choice.")
