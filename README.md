# ToDoLo

A self-contained, glassmorphism to-do app that runs entirely in your browser — no build step, no server, no dependencies. The whole app is a single `index.html` file you can open locally, host on any static site, or install as a PWA on your phone.

> Stay glassy, stay productive.

## Features

- **Multiple lists** with custom colors, alphabetical sort, and drag-and-drop reordering.
- **Smart views** in the sidebar: All, Overdue, Today, Tomorrow, Next 7 Days, and No Date.
- **Rich tasks** — description, due date, recurrence (daily/weekly/monthly), priority, and sub-tasks (checklists).
- **Sub-task behavior** — completed sub-tasks drop to the bottom, finishing them all auto-completes the parent, and recurring tasks reset their sub-tasks to the original order.
- **Powerful filtering & sorting** — combine All/Active/Done with due-date and priority filters, and up to three mixable sort criteria with independent direction.
- **Resizable panels** — drag to resize both the sidebar and the task-detail panel; widths are remembered.
- **Backup & restore** — export all your lists and tasks to a JSON file and import it back.
- **Dropbox sync** — keep the same data on your PC and Android phone through your own Dropbox account (see [setup](#dropbox-sync) below).
- **Installable PWA** — works offline via a service worker, with a home-screen icon and a mobile-optimized layout (slide-in drawer, full-screen task detail, safe-area support).
- **Glassmorphism UI** — frosted-glass panels, themed scrollbars, and smooth animations throughout.

## Getting started

No installation or build is required.

- **Run locally:** open `index.html` in any modern browser. Or serve the folder over a static server (needed for the service worker / PWA features):

  ```bash
  python -m http.server 8766
  # then visit http://localhost:8766
  ```

- **Host it:** drop the files on any static host (GitHub Pages, Netlify, etc.). For PWA install and Dropbox sync, it must be served over **HTTPS** (localhost also counts).

- **Install on Android:** open the hosted URL in Chrome → menu → **Add to Home screen**.

Your data is stored locally in the browser's `localStorage`. Use Backup/restore or Dropbox sync to move it between devices.

## Dropbox sync

Sync runs entirely client-side using OAuth2 PKCE — your data goes straight from your browser to your own Dropbox and never passes through any third-party server.

One-time setup (repeat the connect step on each device):

1. Go to the [Dropbox App Console](https://www.dropbox.com/developers/apps) → **Create app** → **Scoped access** → **App folder** → give it a name.
2. On the **Permissions** tab, enable `files.content.write` and `files.content.read`, then submit.
3. On the **Settings** tab, copy the **App key**, and under **OAuth 2 → Redirect URIs** add the exact URL where you open ToDoLo (e.g. `https://yourname.github.io/todolo/index.html`). HTTPS is required (localhost works too).
4. In ToDoLo → **Settings → Dropbox sync**, paste the App key and click **Connect**. Do the same on your phone with the same key.
5. **Upload** from one device; the other can **Download**, or use the toggles below.

Sync options once connected:

- **Auto-upload** — pushes your changes to Dropbox 10 seconds after you stop editing.
- **Auto-sync** — silently pulls a newer Dropbox backup whenever the app opens.
- **Sync now** — a sidebar button for an instant manual upload, with a spinning indicator while syncing.

## Project structure

| File | Purpose |
| --- | --- |
| `index.html` | The entire app — HTML, CSS, and JavaScript in one file. |
| `sw.js` | Service worker for offline caching (network-first with cache fallback). |
| `manifest.json` | PWA manifest (name, icons, theme, standalone display). |
| `icon.svg` | App icon used by the manifest and favicon. |

## Tech notes

- Pure vanilla HTML/CSS/JavaScript — no frameworks, no build tooling.
- State persists in `localStorage`.
- The service worker uses `skipWaiting` / `clients.claim` so updates take effect promptly; bump the `CACHE` version in `sw.js` when shipping changes.