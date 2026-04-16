"""
main.py — Entry point for the Timetable Manager.

Tabbed main menu:
  Tab 1 → 📋 Timetable   (recurring weekly schedule)
  Tab 2 → 📅 Daily       (day-to-day task manager)
  Tab 3 → 📆 Weekly      (weekly overview + tasks)
  Tab 4 → 🗓️  Monthly     (calendar + events)
"""

from datetime import date
from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich.text    import Text
from rich         import box

import data
import utils
import timetable
import daily
import weekly
import monthly

console = Console()


# ── Dashboard ──────────────────────────────────────────────────────────────────

def show_dashboard():
    """Quick summary shown on the main menu."""
    today     = utils.today_str()
    day_name  = utils.day_name(today)
    tasks     = data.get_tasks(today)
    done      = sum(1 for t in tasks if t["done"])
    pending   = len(tasks) - done
    slots     = data.get_timetable(day_name)

    from datetime import datetime
    ym        = f"{date.today().year:04d}-{date.today().month:02d}"
    events    = data.get_month_events(ym)
    today_evs = [e for e in events if e.get("date") == today]

    # ── Today panel ──
    t = Text()
    t.append(f"\n  📅  Today: ", style="dim")
    t.append(utils.friendly_date(today) + "\n", style="bold white")
    t.append(f"\n  📋  Classes:  ", style="dim")
    t.append(f"{len(slots)} slot(s)\n", style="bold cyan")
    t.append(f"  ✅  Tasks:    ", style="dim")
    t.append(f"{done} done", style="bold green")
    t.append(f"  /  ", style="dim")
    t.append(f"{pending} pending\n", style="bold yellow")
    t.append(f"  🗓️   Events:   ", style="dim")
    t.append(f"{len(today_evs)} today\n", style="bold magenta")

    # Next upcoming task
    upcoming = next((task for task in tasks if not task["done"]), None)
    if upcoming:
        pcolor = {"high": "red", "medium": "yellow", "low": "green"}.get(upcoming["priority"], "white")
        t.append(f"\n  ⚑  Next:  ", style="dim")
        t.append(f"{upcoming['title']}", style=f"bold {pcolor}")
        if upcoming.get("time"):
            t.append(f"  @ {upcoming['time']}", style="dim")
        t.append("\n")

    # Next class
    from datetime import datetime as dt
    now = dt.now().strftime("%H:%M")
    next_class = next((s for s in slots if s["time"] >= now), None)
    if next_class:
        color = next_class.get("color", "cyan")
        t.append(f"\n  📖  Next class:  ", style="dim")
        t.append(f"{next_class['subject']}", style=f"bold {color}")
        t.append(f"  @ {next_class['time']}\n", style="dim")

    console.print(Panel(t, title="[bold cyan]Today's Snapshot[/]",
                        border_style="cyan", expand=True))


# ── Main Menu ──────────────────────────────────────────────────────────────────

def main():
    while True:
        utils.clear()
        # Big header
        console.print()
        console.print(
            Panel(
                Text("📅  TIMETABLE MANAGER", justify="center", style="bold cyan"),
                subtitle="[dim]Your complete schedule organizer[/dim]",
                border_style="cyan",
                expand=True,
            )
        )

        show_dashboard()

        # Tab menu
        tab_table = Table(box=box.SIMPLE, show_header=False, expand=True, border_style="dim")
        tab_table.add_column(justify="center", style="bold cyan",    min_width=22)
        tab_table.add_column(justify="center", style="bold green",   min_width=22)
        tab_table.add_column(justify="center", style="bold blue",    min_width=22)
        tab_table.add_column(justify="center", style="bold magenta", min_width=22)
        tab_table.add_row(
            "[ 1 ]  📋  Timetable",
            "[ 2 ]  📅  Daily",
            "[ 3 ]  📆  Weekly",
            "[ 4 ]  🗓️   Monthly",
        )
        console.print(tab_table)
        console.print("  [dim]0.[/] Exit\n")

        choice = utils.prompt("Select Tab")

        if   choice == "1": timetable.menu()
        elif choice == "2": daily.menu()
        elif choice == "3": weekly.menu()
        elif choice == "4": monthly.menu()
        elif choice == "0":
            utils.clear()
            console.print("\n  [bold cyan]Goodbye! See you tomorrow. 👋[/]\n")
            break
        else:
            utils.error("Enter 1, 2, 3, 4 or 0.")


if __name__ == "__main__":
    main()
