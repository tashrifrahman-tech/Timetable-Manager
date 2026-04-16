"""
monthly.py — Monthly calendar and event manager (Tab 4).

Features:
  • Visual calendar grid for any month
  • Color-coded events per day
  • Add / delete events with title, date, time, description
  • Monthly stats: total events, busiest day
  • Navigate prev/next months
"""

import calendar
from datetime import datetime, date
from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich.text    import Text
from rich         import box

import data
import utils

console = Console()

DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ── Calendar view ──────────────────────────────────────────────────────────────

def view_month(year: int, month: int):
    month_name = datetime(year, month, 1).strftime("%B %Y")
    utils.header(f"🗓️   {month_name}", "Monthly Calendar & Events", "magenta")

    today = date.today()
    ym    = utils.month_key(year, month)
    events = data.get_month_events(ym)

    # Build a quick lookup: day_number -> list of event titles
    day_events: dict[int, list] = {}
    for ev in events:
        try:
            d = datetime.strptime(ev["date"], "%Y-%m-%d").day
            day_events.setdefault(d, []).append(ev)
        except ValueError:
            pass

    # Also include tasks
    grid = utils.month_matrix(year, month)
    tasks_by_day: dict[int, int] = {}
    for week in grid:
        for cell in week:
            if cell:
                ts = data.get_tasks(cell.isoformat())
                if ts:
                    tasks_by_day[cell.day] = len(ts)

    # ── Calendar table ──
    cal_table = Table(box=box.ROUNDED, border_style="magenta",
                      expand=True, show_header=True)
    for h in DAY_HEADERS:
        is_weekend = h in ("Sat", "Sun")
        cal_table.add_column(h, justify="center",
                             style="dim red" if is_weekend else "cyan",
                             min_width=13)

    for week in grid:
        cells = []
        for cell in week:
            if cell is None:
                cells.append("")
            else:
                is_today = (cell == today)
                evs      = day_events.get(cell.day, [])
                n_tasks  = tasks_by_day.get(cell.day, 0)

                t = Text(justify="center")
                # Day number
                if is_today:
                    t.append(f" ★ {cell.day:2d} ★ ", style="bold white on magenta")
                else:
                    t.append(f"  {cell.day:2d}  ", style="bold white")
                t.append("\n")

                # Events (up to 2)
                for ev in evs[:2]:
                    color = ev.get("color", "magenta")
                    t.append(f"• {ev['title'][:10]}\n", style=f"bold {color}")
                if len(evs) > 2:
                    t.append(f"+{len(evs)-2} more\n", style="dim")

                # Task count
                if n_tasks:
                    t.append(f"[{n_tasks} task{'s' if n_tasks>1 else ''}]\n", style="dim green")

                cells.append(t)
        cal_table.add_row(*cells)

    console.print(cal_table)

    # ── Event list ──
    if events:
        console.print()
        ev_table = Table(box=box.SIMPLE, border_style="magenta",
                         title=f"[bold magenta]Events in {month_name}[/]", expand=True)
        ev_table.add_column("ID",    style="dim",    width=4)
        ev_table.add_column("Date",  style="white",  width=12)
        ev_table.add_column("Time",  style="white",  width=7)
        ev_table.add_column("Title", style="bold magenta", min_width=20)
        ev_table.add_column("Description", style="dim", min_width=20)

        for ev in events:
            try:
                date_fmt = datetime.strptime(ev["date"], "%Y-%m-%d").strftime("%d %b")
            except Exception:
                date_fmt = ev["date"]
            color = ev.get("color", "magenta")
            ev_table.add_row(
                str(ev["id"]),
                date_fmt,
                ev.get("time", "—"),
                f"[bold {color}]{ev['title']}[/]",
                ev.get("desc", ""),
            )
        console.print(ev_table)
    else:
        utils.info(f"No events this month. Add one with option 1.")

    # ── Stats ──
    total = len(events)
    if total:
        busiest_day = max(day_events, key=lambda d: len(day_events[d]))
        console.print(
            f"\n  [dim]This month:[/] [bold]{total}[/] event(s)  |  "
            f"[magenta]Busiest day: {busiest_day} {month_name}[/]"
        )


# ── Actions ───────────────────────────────────────────────────────────────────

def add_event(year: int, month: int):
    utils.header("➕  Add Event", "", "green")

    title = utils.prompt("Event title")
    if not title:
        utils.error("Title cannot be empty.")
        utils.pause()
        return

    default_date = utils.month_key(year, month) + f"-01"
    date_str = utils.ask_date("Date (YYYY-MM-DD)", default_date)
    time_val = utils.ask_time("Time (HH:MM, optional)", "")
    desc     = utils.prompt("Description (optional)")
    color    = utils.pick_color("Event color")

    ym = utils.month_key(year, month)
    data.add_event(ym, title, date_str, time_val, desc, color)
    utils.success(f"Event '{title}' added on {date_str}.")
    utils.pause()


def delete_event(year: int, month: int):
    ym     = utils.month_key(year, month)
    events = data.get_month_events(ym)
    if not events:
        utils.info("No events to delete.")
        utils.pause()
        return

    raw = utils.prompt("Enter event ID to delete")
    try:
        event_id = int(raw)
    except ValueError:
        utils.error("Invalid ID.")
        utils.pause()
        return

    if data.delete_event(ym, event_id):
        utils.success("Event deleted.")
    else:
        utils.error("Event not found.")
    utils.pause()


# ── Menu ───────────────────────────────────────────────────────────────────────

def menu():
    today = date.today()
    year, month = today.year, today.month

    while True:
        view_month(year, month)
        console.print()
        console.print("  [bold cyan]1.[/] ➕  Add Event")
        console.print("  [bold cyan]2.[/] 🗑️   Delete Event")
        console.print("  [bold cyan]3.[/] ◀   Previous Month")
        console.print("  [bold cyan]4.[/] ▶   Next Month")
        console.print("  [bold cyan]5.[/] 🏠  This Month")
        console.print("  [bold cyan]6.[/] 🔍  Jump to Month")
        console.print("  [bold cyan]0.[/] ← Back to Main Menu")

        choice = utils.prompt("Choice")

        if   choice == "1": add_event(year, month)
        elif choice == "2": delete_event(year, month)
        elif choice == "3":
            month -= 1
            if month == 0:
                month, year = 12, year - 1
        elif choice == "4":
            month += 1
            if month == 13:
                month, year = 1, year + 1
        elif choice == "5":
            year, month = today.year, today.month
        elif choice == "6":
            raw_y = utils.prompt("Year (e.g. 2025)", str(year))
            raw_m = utils.prompt("Month 1-12", str(month))
            try:
                year  = int(raw_y)
                month = max(1, min(12, int(raw_m)))
            except ValueError:
                utils.error("Invalid year/month.")
        elif choice == "0":
            break
        else:
            utils.error("Invalid choice.")
