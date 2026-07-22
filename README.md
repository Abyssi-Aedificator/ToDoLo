# ToDoLo

A self-contained, glassmorphism-style to-do app that runs entirely in the browser (no server, no build step).

## Features

- **Multiple lists** with colour coding and drag-to-reorder
- **Smart views** — All, In Progress, Paused, Overdue, Today, Tomorrow, Next 7 Days, No Date
- **Task details** — title, description, due date, recurrence (daily/weekly/monthly), priority, tags, sub-tasks
- **Sub-tasks** with drag-to-reorder and auto-complete when all are done
- **Filtering** — by status, due date, priority, tag, and free-text search
- **Sorting** — by due date, priority, title, created date, recurrence, sub-task progress, list name; up to 3 levels with direction toggles
- **Recurring tasks** — due date rolls forward on completion; sub-tasks reset
- **Task statuses** — Todo, In Progress, Paused, Won't Do (with badges)
- **Right-click context menu** — Won't Do, Set In Progress, Pause, Skip, Due Today
- **Quick Open** — `Cmd+K` / `Ctrl+K` command palette for fast search
- **Themes** — light/dark mode + 6 colour accents (teal, blue, purple, pink, orange, green)
- **Backup & restore** — export/import to a JSON file
- **Dropbox sync** — client-side OAuth2 PKCE; syncs between devices with no backend
- **Offline-capable PWA** — service worker caches all assets
- **Fully client-side** — data stored in `localStorage`

## Usage

Open `index.html` in any modern browser. No build steps, no dependencies.

## License

MIT
