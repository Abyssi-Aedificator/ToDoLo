# AGENTS.md

## Project

Single-file browser app. All CSS, HTML, and JS live in `index.html` (~3900 lines). No build step, no dependencies, no server required — open `index.html` in a browser.

## Key commands

There are none. Edit `index.html` directly. Refresh the browser to see changes. The service worker (`sw.js`) caches aggressively — use hard refresh (Ctrl+Shift+R) or disable cache in DevTools during development.

## Architecture

- `index.html` — the entire app: CSS (lines ~1–1060), HTML (lines ~1060–1460), JS (lines ~1460–3900)
- `sw.js` — service worker, caches assets under `CACHE = 'todolo-v4'`; bump the cache name after changing any asset
- `manifest.json` — PWA manifest, icons point to `icon.svg`
- `icon.svg` — app icon
- All user data is stored in `localStorage` (key: `glass-todos-data`)
- State object: `state = { activeId, lists: [...] }` — persisted on every mutation via `save()`

## Versioning & changelog

- `APP_VERSION` constant (line ~1852) and the first entry in the changelog `<div class="changelog">` must stay in sync
- `DEV = true` shows a red dev banner — set to `false` before release
- Changelog lives inline in the settings modal HTML; new entry goes at the top of `<div class="changelog">`

## Mobile responsive breakpoint

- `@media (max-width: 720px)` — sidebar becomes a slide-in drawer, detail panel goes full-screen
- `--panel-solid` — mobile panel background (dark `rgba(20,40,50,0.94)`, light `rgba(248,250,252,0.94)`); prevents list bleed-through on mobile

## Gotchas

- `createGlassSelect()` returns an object with a `.value` getter/setter — not a DOM element
- `dueFilter` and `prioFilter` are plain strings (not glass-select objects); `tagFilter`, `sortBy`, `sortBy2`, `sortBy3` are glass-select objects
- The `sortDir` button toggles a `.desc` class on itself — CSS handles the arrow flip
- After editing, check that no stale references remain to removed IDs (especially after HTML restructuring)
