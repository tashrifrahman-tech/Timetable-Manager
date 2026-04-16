# 📅 Timetable Manager

---

## ✨ Features at a Glance

| Feature | Details |
|---|---|
| **4 Tabbed Views** | Timetable · Daily · Weekly · Monthly — all navigable from one menu |
| **Live Dashboard** | Today's snapshot on startup — next class, next task, pending count |
| **Recurring Timetable** | Set a fixed weekly class schedule with color-coded subjects |
| **Daily Task Manager** | Add tasks with priority, time, and description; mark done/undone |
| **Daily Notes** | Attach a free-text note to any date |
| **Weekly Overview** | Full week at a glance with per-day progress bars |
| **Monthly Calendar** | Visual calendar grid with events overlaid on each date cell |
| **Color Coding** | 7 colors for subjects and events (cyan, green, yellow, magenta, red, blue, white) |
| **Priority Levels** | High 🔴 · Medium 🟡 · Low 🟢 with color-coded display |
| **Date Navigation** | Jump to any date, step through days/weeks/months freely |
| **Persistent Storage** | All data saved to a local `data.json` file automatically |

---

## 🗂️ Project Structure

```
Timetable-Manager/
│
├── main.py          # Entry point — main menu + today's dashboard
├── timetable.py     # Tab 1 — Recurring weekly class schedule
├── daily.py         # Tab 2 — Day-to-day task manager
├── weekly.py        # Tab 3 — Weekly overview with progress bars
├── monthly.py       # Tab 4 — Monthly calendar + event manager
│
├── data.py          # All JSON read/write operations
├── utils.py         # Rich display helpers, input prompts, date utilities
│
├── requirements.txt # Python dependencies
└── data.json        # Auto-created on first run — your stored data
```

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10 or higher**
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Timetable-Manager.git
cd Timetable-Manager

# 2. Install the only dependency
pip install rich

# 3. Run the app
python main.py
```

> That's it — no database setup, no config files, no accounts.

---

## 🖥️ How to Use

When you launch the app, you'll see a **dashboard** showing today's snapshot, then a tab menu:

```
[ 1 ]  📋  Timetable    [ 2 ]  📅  Daily    [ 3 ]  📆  Weekly    [ 4 ]  🗓️  Monthly
```

Type the tab number and press Enter to enter that section.

---

### 📋 Tab 1 — Timetable

Your **recurring weekly class schedule** — the same every week.

**What you can do:**
- View the full week as a formatted table (all 7 days, sorted by time)
- View a single day's schedule
- Add a new class slot (day, time, subject, room, color)
- Edit an existing slot by its ID
- Delete a slot

**Example — Adding a slot:**
```
> Choose day: 1 (Monday)
> Class time (HH:MM): 09:00
> Subject / Class name: Mathematics
> Location / Room (optional): Room 101
> Pick a color: 1 (Cyan)
✓ Added 'Mathematics' at 09:00 on Monday.
```

---

### 📅 Tab 2 — Daily Manager

Your **day-to-day planner**. Defaults to today; navigate freely to any date.

**What you can do:**
- See today's timetable and tasks side-by-side in two panels
- Add tasks with title, description, priority, and optional time
- Mark tasks done/undone (toggles with strikethrough display)
- Delete tasks
- Write or edit a daily note
- Navigate ◀ previous day / ▶ next day
- Jump directly to any date (YYYY-MM-DD)
- Return to today instantly with option 8

**Task priorities:**
- 🔴 **High** — shown in red
- 🟡 **Medium** — shown in yellow
- 🟢 **Low** — shown in green

---

### 📆 Tab 3 — Weekly Overview

A **bird's-eye view** of the entire current week.

**What you can do:**
- See a table with 7 day columns showing timetable slots + tasks per day
- View a per-day **progress bar** (e.g. `████░░░░░░  2/5`)
- See weekly stats: total tasks, done, pending, high-priority pending
- Add a task to any day in the displayed week
- Toggle a task done/undone for any day
- Navigate ◀ previous week / ▶ next week

**Progress bar colors:**
- 🟢 Green — all tasks complete
- 🟡 Yellow — partially complete
- ⬜ Dim — no tasks / none done

---

### 🗓️ Tab 4 — Monthly Calendar

A **full calendar grid** for any month with events overlaid on dates.

**What you can do:**
- View a calendar grid (Mon–Sun) with events and task counts shown in each cell
- Today's date is highlighted with a ★ star marker
- Weekend columns are displayed in a different color
- Add an event (title, date, time, description, color)
- Delete an event by its ID
- View the full event list for the month below the calendar
- See monthly stats: total events, busiest day
- Navigate ◀ previous month / ▶ next month
- Jump directly to any year and month

---

## 💾 Data Storage

All data is stored in a single `data.json` file in the project directory, created automatically on first run. The structure is:

```json
{
  "timetable": {
    "Monday": [
      { "id": 1, "time": "09:00", "subject": "Mathematics", "location": "Room 101", "color": "cyan" }
    ],
    "Tuesday": [ ... ]
  },
  "tasks": {
    "2025-04-14": [
      { "id": 1, "title": "Complete assignment", "desc": "Chapter 5", "priority": "high", "time": "15:00", "done": false }
    ]
  },
  "events": {
    "2025-04": [
      { "id": 1, "title": "Mid-term Exam", "date": "2025-04-20", "time": "09:00", "desc": "Mathematics", "color": "red" }
    ]
  },
  "notes": {
    "2025-04-14": "Remember to bring lab coat tomorrow."
  }
}
```

> 💡 You can back up your data by simply copying `data.json`.

---

## 🏗️ Code Architecture

The project is split into focused, single-responsibility modules:

| Module | Responsibility |
|---|---|
| `main.py` | App entry point, main menu loop, today's dashboard rendering |
| `timetable.py` | All UI and logic for the recurring weekly schedule (Tab 1) |
| `daily.py` | Daily task manager with side-by-side timetable+task view (Tab 2) |
| `weekly.py` | Weekly summary table with progress bars (Tab 3) |
| `monthly.py` | Calendar grid builder and event manager (Tab 4) |
| `data.py` | Pure data layer — all JSON read/write, zero UI code |
| `utils.py` | Shared helpers: Rich display, input prompts, date utilities |

**Key design principles used:**
- **Separation of concerns** — `data.py` contains zero display logic; UI modules contain zero file I/O
- **Single source of truth** — all data goes through `data.load()` and `data.save()`
- **Forward compatibility** — `data.load()` fills in missing keys automatically so old `data.json` files don't break on updates
- **Auto-incrementing IDs** — each record type uses `_next_id()` to assign stable integer IDs for edit/delete operations

---

## 🐍 Concepts Practiced

This project is a great exercise in:

- **File I/O** — reading and writing structured JSON data
- **Modules** — splitting a project across multiple `.py` files with clean imports
- **CLI design** — building navigable multi-level menus
- **Date/time handling** — `datetime`, `date`, `timedelta`, `calendar` module
- **List comprehensions and filtering** — used throughout `data.py`
- **Error handling** — graceful handling of invalid input, malformed JSON, empty states
- **Rich library** — tables, panels, columns, text styling, color markup

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| [rich](https://github.com/Textualize/rich) | ≥ 13.0.0 | Terminal formatting, tables, panels, color |

No database, no internet connection, no API keys required.

---

## 🔮 Possible Future Improvements

- Export timetable/tasks to CSV or PDF
- Recurring tasks (e.g. "every Monday")
- Search tasks by keyword across all dates
- Desktop notifications / reminders using `plyer`
- Import timetable from a `.csv` file
- Multi-user support with named profiles

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🙋 Author

Built as part of a Python learning journey — progressing from CLI basics to structured, multi-module applications.

If you found this useful, consider giving it a ⭐ on GitHub!
