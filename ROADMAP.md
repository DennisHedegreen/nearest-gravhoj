# Roadmap

## v1.1 — access layer (dev, in progress)
- Overpass-based spatial join for public access classification
- Three categories: always / daylight / unknown
- Access shown in result card

## v1.2 — nearest N
- Show nearest 3–5 gravhøje instead of only 1
- Ranked by distance
- Quick tap to switch between results
- Useful when nearest is on inaccessible land

## v1.3 — filter by access
- Toggle to show only always / daylight / both
- No new UI elements beyond a simple filter control
- Depends on v1.1 access data being solid

## v2.0 — collector model
- User-reported quality layer: "besøgt", "god stand", "svær adgang", "lukket"
- Community curation on top of the official dataset
- Enables the samler mechanic: people collect gravhøje over time
- Requires decisions on: storage model, identity model, moderation

## Internal track (not public)
- Batch quality scoring pass: identify gravhøje likely worth visiting based on
  datering (Bronzealder/Vikingetid rarer than Oldtid), access category, and
  proximity to known hiking routes
- Internal ranked export for editorial use on Hedegreen Research
- Not a public feature — internal research infrastructure

## Long-term
- Archive mode: personal log of visited gravhøje (local-first, no account)
- Visual differentiation between access categories on a map view
- Seasonal access notes (some protected areas have bird nesting restrictions)
