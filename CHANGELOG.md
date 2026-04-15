# Changelog

## v1.1 — dev (2026-04-16)

### Access layer
- Added Overpass API fetch script (`scripts/fetch_adgang.py`) for Danish forest and nature area polygons
- Added spatial join script (`scripts/join_access.py`) using shapely STRtree for point-in-polygon lookup against 180,000+ OSM polygons
- Added `access` field to slim JSON with three categories: `always`, `daylight`, `unknown`
- Access classification follows naturbeskyttelsesloven: Naturstyrelsen areas and nature reserves → always, private forests → daylight, no match → unknown
- App now shows access status in the existing meta line on the result card
- Added `requirements.txt` with shapely dependency
- Added `data/adgang.raw.geojson` to `.gitignore`

### Results
- 203 gravhøje classified as always accessible
- 12,499 classified as daylight access (private forest)
- 11,819 classified as unknown (likely private agricultural land or enclosed areas)

---

## v1.0 — main (2026-03-20)

### Launch
- Initial public release at dennishedegreen.github.io/nearest-gravhoj
- Browser geolocation + haversine distance against local dataset
- 24,520 fredede rundhøje from Fund og Fortidsminder WFS (Slots- og Kulturstyrelsen)
- Single nearest result with distance, metadata, route link, and official source link
- Static deployment on GitHub Pages — no backend, no tracking
