# nearest-gravhoj

Find the nearest registered Danish gravhøj from your current location.

Live app:

- https://dennishedegreen.github.io/nearest-gravhoj/

Repository:

- https://github.com/DennisHedegreen/nearest-gravhoj

## What it does

This is a very small public tool.

It does one thing:

- uses your browser location
- finds the nearest registered gravhøj in a local filtered dataset
- shows basic information
- hands off to directions and the official source entry

It is not a heritage portal.
It is not a full archaeology database.
It is a one-button field tool for people who are simply curious and out on a trip.

## How to use it

1. Open the live app.
2. Allow location access in the browser.
3. Press `Find nærmeste gravhøj`.
4. Open the route or the official source entry.

## Important note

Nearest does not automatically mean publicly accessible.

Some gravhøje are on private land or can only be viewed from public areas.
The app helps you find the nearest registered site.
It does not guarantee physical access.

## Data source

The current version uses a local filtered extract from the official Danish
`Fund og Fortidsminder` dataset from Slots- og Kulturstyrelsen / Kulturarv.

Current v1 slice:

- fredede point features
- filtered to `anlaegstype = Rundhøj`
- `24,520` entries in the local extract

Why a local extract:

- faster lookup
- no runtime dependency on the public WFS
- simpler static deployment

## Run locally

Refresh the local data file:

```bash
python3 nearest-gravhoj/scripts/fetch_rundhoje.py
```

Serve the app locally from the repo root:

```bash
python3 -m http.server 8765 --directory nearest-gravhoj
```

Then open:

```text
http://127.0.0.1:8765/
```

## Files

- `index.html` for the public one-page interface
- `app.js` for the browser-side lookup logic
- `styles.css` for the visual layer
- `data/rundhoje.min.json` for the local filtered dataset
- `scripts/fetch_rundhoje.py` for refreshing the data from the official WFS

## Project note

This tool was built inside Hedegreen Research.
The point was to keep the first version small enough to finish.
