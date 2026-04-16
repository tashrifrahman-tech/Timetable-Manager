"""
timetable.py — Recurring weekly timetable manager (Tab 1).

Lets the user define a fixed weekly schedule:
  Add / Edit / Delete time slots per day.
  View the full week as a formatted table.
"""

from rich.console import Console
from rich.table   import Table
from rich         import box

import data
import utils

console = Console()


# ── Views ──────────────────────────────────────────────────────────────────────

def view_week():
    """Print the full weekly timetable as a rich table."""
    utils.header("📋  Weekly Timetable", "Your recurring class / work schedule", "cyan")

    table = Table(box=box.ROUNDED, border_style="cyan", show_header=True, expand=True)
    table.add_column("Day", style="bold cyan", width=12)
    table.add_column("Time",    style="white",   width=8)
    table.add_column("Subject / Class", style="bold white", min_width=20)
    table.add_column("Location", style="dim white", width=14)
    table.add_column("ID", style="dim", width=4)

    for day in data.DAYS:
        slots = data.get_timetable(day)
        if not slots:
            table.add_row(f"[bold]{day}[/]", "[dim]—[/]", "[dim]No classes[/]", "", "")
        else:
            for i, slot in enumerate(slots):
                color   = slot.get("color", "cyan")
                day_lbl = f"[bold]{day}[/]" if i == 0 else ""
                table.add_row(
                    day_lbl,
                    f"[white]{slot['time']}[/]",
                    f"[bold {color}]{slot['subject']}[/]",
                    f"[dim]{slot.get('location', '')}[/]",
                    f"[dim]{slot['id']}[/]",
                )

    console.print(table)


def view_day(day: str):
    """Print slots for one day."""
    utils.header(f"📋  {day} Timetable", "", "cyan")
    slots = data.get_timetable(day)

    if not slots:
        utils.info(f"No slots added for {day} yet.")
        return

    table = Table(box=box.SIMPLE_HEAVY, border_style="cyan", expand=True)
    table.add_column("ID",      style="dim",        width=4)
    table.add_column("Time",    style="bold white",  width=8)
    table.add_column("Subject", style="bold cyan",   min_width=20)
    table.add_column("Location",style="dim white",   width=16)

    for slot in slots:
        color = slot.get("color", "cyan")
        table.add_row(
            str(slot["id"]),
            slot["time"],
            f"[bold {color}]{slot['subject']}[/]",
            slot.get("location", "—"),
        )

    console.print(table)


# ── Actions ────────────────────────────────────────────────────────────────────

def _pick_day() -> str | None:
    idx = utils.pick_from(data.DAYS, "Choose day")
    return data.DAYS[idx] if idx is not None else None


def add_slot():
    utils.header("➕  Add Timetable Slot", "", "green")
    day = _pick_day()
    if not day:
        return

    time    = utils.ask_time("Class time (HH:MM)")
    subject = utils.prompt("Subject / Class name")
    if not subject:
        utils.error("Subject cannot be empty.")
        return
    location = utils.prompt("Location / Room (optional)")
    color    = utils.pick_color("Highlight color")

    data.add_slot(day, time, subject, location, color)
    utils.success(f"Added '{subject}' at {time} on {day}.")
    utils.pause()


def edit_slot():
    utils.header("✏️   Edit Timetable Slot", "", "yellow")
    day = _pick_day()
    if not day:
        return

    view_day(day)
    slots = data.get_timetable(day)
    if not slots:
        utils.pause()
        return

    raw = utils.prompt("Enter slot ID to edit")
    try:
        slot_id = int(raw)
    except ValueError:
        utils.error("Invalid ID.")
        utils.pause()
        return

    slot = next((s for s in slots if s["id"] == slot_id), None)
    if not slot:
        utils.error("Slot not found.")
        utils.pause()
        return

    utils.info("Leave blank to keep current value.")
    new_time     = utils.ask_time(f"Time [{slot['time']}]", slot["time"])
    new_subject  = utils.prompt(f"Subject [{slot['subject']}]") or slot["subject"]
    new_location = utils.prompt(f"Location [{slot.get('location','')}]") or slot.get("location", "")
    new_color    = utils.pick_color("New color") or slot.get("color", "cyan")

    data.edit_slot(day, slot_id, time=new_time, subject=new_subject,
                   location=new_location, color=new_color)
    utils.success("Slot updated.")
    utils.pause()


def delete_slot():
    utils.header("🗑️   Delete Timetable Slot", "", "red")
    day = _pick_day()
    if not day:
        return

    view_day(day)
    slots = data.get_timetable(day)
    if not slots:
        utils.pause()
        return

    raw = utils.prompt("Enter slot ID to delete")
    try:
        slot_id = int(raw)
    except ValueError:
        utils.error("Invalid ID.")
        utils.pause()
        return

    if data.delete_slot(day, slot_id):
        utils.success("Slot deleted.")
    else:
        utils.error("Slot not found.")
    utils.pause()


# ── Menu ───────────────────────────────────────────────────────────────────────

def menu():
    while True:
        utils.header("📋  Timetable Manager", "Manage your recurring weekly schedule", "cyan")
        console.print()
        console.print("  [bold cyan]1.[/] 📅  View Full Week")
        console.print("  [bold cyan]2.[/] 📆  View Single Day")
        console.print("  [bold cyan]3.[/] ➕  Add Slot")
        console.print("  [bold cyan]4.[/] ✏️   Edit Slot")
        console.print("  [bold cyan]5.[/] 🗑️   Delete Slot")
        console.print("  [bold cyan]0.[/] ← Back to Main Menu")

        choice = utils.prompt("Choice")

        if   choice == "1": view_week();        utils.pause()
        elif choice == "2":
            day = _pick_day()
            if day:
                view_day(day)
                utils.pause()
        elif choice == "3": add_slot()
        elif choice == "4": edit_slot()
        elif choice == "5": delete_slot()
        elif choice == "0": break
        else: utils.error("Invalid choice.")
