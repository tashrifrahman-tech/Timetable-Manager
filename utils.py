"""
utils.py — Shared display helpers and input utilities using Rich.
"""

from datetime import datetime, date, timedelta
from rich.console import Console
from rich.panel   import Panel
from rich.text    import Text
from rich import box

console = Console()

APP_TITLE = "📅  T I M E T A B L E  M A N A G E R"

PRIORITY_STYLE = {
    "high":   "bold red",
    "medium": "bold yellow",
    "low":    "bold green",
}

MENU_STYLE = "bold cyan"

# ── Generic helpers ────────────────────────────────────────────────────────────

def clear():
    console.clear()


def header(title: str, subtitle: str = "", color: str = "cyan"):
    clear()
    t = Text(justify="center")
    t.append(f"\n{APP_TITLE}\n", style="bold cyan")
    t.append(f"{title}\n", style=f"bold {color}")
    if subtitle:
        t.append(subtitle, style="dim")
    console.print(Panel(t, border_style=color, expand=True))


def rule(color: str = "cyan"):
    console.rule(style=color)


def success(msg: str):
    console.print(f"\n  [bold green]✓[/] {msg}")


def error(msg: str):
    console.print(f"\n  [bold red]✗[/] {msg}")


def info(msg: str):
    console.print(f"\n  [dim cyan]ℹ[/] {msg}")


def prompt(msg: str, default: str = "") -> str:
    try:
        val = console.input(f"\n  [bold cyan]>[/] {msg}: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        return default


def pause():
    try:
        console.input("\n  [dim]Press Enter to continue...[/]")
    except (EOFError, KeyboardInterrupt):
        pass


def pick_from(options: list[str], label: str = "Choose") -> int | None:
    """Show numbered list, return 0-based index or None on cancel."""
    console.print()
    for i, opt in enumerate(options, 1):
        console.print(f"  [bold cyan]{i}.[/] {opt}")
    console.print(f"  [dim]0. Cancel[/]")
    raw = prompt(label)
    try:
        n = int(raw)
        if n == 0:
            return None
        if 1 <= n <= len(options):
            return n - 1
    except ValueError:
        pass
    error("Invalid choice.")
    return None


def pick_priority() -> str:
    idx = pick_from(["🔴 High", "🟡 Medium", "🟢 Low"], "Priority")
    return ["high", "medium", "low"][idx] if idx is not None else "medium"


def pick_color(label: str = "Pick a color") -> str:
    from data import COLORS
    idx = pick_from([f"[{c}]{c.capitalize()}[/{c}]" for c in COLORS], label)
    return COLORS[idx] if idx is not None else "cyan"


def ask_time(label: str = "Time (HH:MM)", default: str = "") -> str:
    while True:
        val = prompt(label, default)
        if not val:
            return default
        try:
            datetime.strptime(val, "%H:%M")
            return val
        except ValueError:
            error("Use HH:MM format (e.g. 09:30)")


def ask_date(label: str = "Date (YYYY-MM-DD)", default: str = "") -> str:
    if not default:
        default = date.today().isoformat()
    while True:
        val = prompt(label, default)
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            error("Use YYYY-MM-DD format (e.g. 2025-06-15)")


# ── Date helpers ───────────────────────────────────────────────────────────────

def today_str() -> str:
    return date.today().isoformat()


def week_dates(offset: int = 0) -> list[str]:
    """Return ISO date strings for Mon–Sun of the current week + offset weeks."""
    today  = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    return [(monday + timedelta(days=i)).isoformat() for i in range(7)]


def month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def days_in_month(year: int, month: int) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]


def month_matrix(year: int, month: int) -> list[list]:
    """Return a 6×7 grid of date objects (or None) for a calendar month."""
    import calendar
    cal = calendar.monthcalendar(year, month)
    grid = []
    for week in cal:
        row = [date(year, month, d) if d != 0 else None for d in week]
        grid.append(row)
    return grid


def day_name(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")


def friendly_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %d %B %Y")
