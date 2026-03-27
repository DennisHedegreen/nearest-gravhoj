# nearest-gravhoj

Working project for a very small archaeology-adjacent public tool.

Public idea:

`Show me the nearest gravhøj.`

Not a full archaeology platform.
Not a heritage portal.
Not a giant map project.

The point is to keep the first version narrow:

- use current location
- find the nearest gravhøj / fortidsminde
- show basic context
- optionally show route or map

## Why this exists

It follows the same pattern that made Danish Politics Data real:

- one clear question
- public data
- simple interface
- immediate usefulness

It also carries the first domain-adjacent feedback from outside the politics tool world:
an archaeologist immediately understood the value of making data readable this way.

## Current status

Small working v1 now exists:

- `index.html` + `styles.css` + `app.js`
- local filtered data file in `data/rundhoje.min.json`
- ingest script in `scripts/fetch_rundhoje.py`

Official data source is viable:

- `Fund og Fortidsminder` from Slots- og Kulturstyrelsen / Kulturarv
- full national download package (`FF.zip`) is about `107.7 MB` zipped
- official WFS point layer for fredede fortidsminder contains `35,118` point features
- filtering `anlaegstype = Rundhøj` in the fredede point layer returns `24,520` features
- the current slim local JSON extract is about `2.46 MB` raw and about `0.40 MB` gzipped

This means v1 does not need the whole dataset live in the app.
The current build uses a local extract for `Rundhøj` points instead of querying the public WFS on every user lookup.

## Current v1

The current app does four things:

- loads a local filtered Rundhøj dataset
- asks for current browser location
- calculates the nearest registered Rundhøj locally
- shows one nearest result with basic info and route/source links

It also links out to:

- the official Kulturarv source entry
- Google Maps directions

And it now states one important limit directly in the UI:

- nearest is not the same as publicly accessible
- some sites may sit on private land or only be viewable from public areas
- v1 is a one-button nearest-lookup tool, not yet an access-classification tool

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

## Mobile testing

For real mobile browser testing, the app should be served over `https`.

That means the practical next step is not more app logic, but publication on:

- GitHub Pages
- or another simple static `https` host

If GPS is faked on the phone itself, the existing one-button flow should be enough once the app is opened on a proper `https` URL.

## First questions

- Which exact subset should v1 use: only `Rundhøj` in the fredede point layer, or a broader fortidsminde definition?
- What is the smallest honest scope for v1?
- Should v1 be mobile-first from the beginning?
- Is the public name Danish, English, or both?
- Should the app ship with a local prefiltered file, or refresh periodically from the official WFS?
- Should v1 keep Google Maps directions, or switch to a more neutral mapping link?

## Rule

Keep it small enough to finish.
