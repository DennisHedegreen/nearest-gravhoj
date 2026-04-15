#!/usr/bin/env python3
"""
Fetch Danish public-access areas from OpenStreetMap via Overpass API.
Saves a local GeoJSON cache for use in the access join step.

Source: OpenStreetMap / Overpass API (overpass-api.de)

Access categories produced:
  'always'   - always publicly accessible
               (Naturstyrelsen state forests, nature reserves, national parks,
                beaches/coasts, heaths, bogs under §14-22 naturbeskyttelsesloven)
  'daylight' - accessible sunrise to sunset
               (private forests under §25 naturbeskyttelsesloven)
  'unknown'  - no polygon match found (likely private agricultural land)

Classification logic:
  - operator=Naturstyrelsen + forest/wood → always
  - boundary=national_park → always
  - leisure=nature_reserve + access != private/no → always
  - landuse=forest / natural=wood (private, no Naturstyrelsen operator) → daylight
  - No match → unknown
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Denmark bounding box: south, west, north, east
DK_BBOX = "54.56,8.08,57.75,15.19"

ROOT = Path(__file__).resolve().parents[1]
ADGANG_PATH = ROOT / "data" / "adgang.raw.geojson"

# Overpass query: fetch forest and nature areas within Denmark bounding box.
# Uses out geom to get polygon coordinates inline.
OVERPASS_QUERY = f"""
[out:json][timeout:300][bbox:{DK_BBOX}];
(
  way["landuse"="forest"];
  relation["landuse"="forest"];
  way["natural"="wood"];
  relation["natural"="wood"];
  way["leisure"="nature_reserve"];
  relation["leisure"="nature_reserve"];
  way["boundary"="national_park"];
  relation["boundary"="national_park"];
  way["boundary"="protected_area"]["protect_class"~"^(1|2|3|4|5|6)$"];
  relation["boundary"="protected_area"]["protect_class"~"^(1|2|3|4|5|6)$"];
);
out geom qt;
"""


def classify(tags: dict) -> str:
    landuse = tags.get("landuse", "")
    natural = tags.get("natural", "")
    leisure = tags.get("leisure", "")
    boundary = tags.get("boundary", "")
    operator = tags.get("operator", "").lower()
    access = tags.get("access", "")

    # Explicit no-access
    if access in ("private", "no"):
        return "unknown"

    # National parks and protected areas → always
    if boundary in ("national_park", "protected_area"):
        return "always"

    # Nature reserves → always (unless explicitly private)
    if leisure == "nature_reserve":
        return "always"

    # Naturstyrelsen-operated forests → always accessible
    if "naturstyrelsen" in operator or "naturerhverv" in operator:
        return "always"

    # Municipality or state-owned forests → always
    if tags.get("ownership") in ("public", "national", "municipal"):
        return "always"
    if tags.get("government") in ("forestry",):
        return "always"

    # Private or untagged forest/wood → daylight (§25 naturbeskyttelsesloven)
    if landuse == "forest" or natural == "wood":
        return "daylight"

    return "unknown"


def overpass_to_geojson(elements: list) -> list:
    """Convert Overpass elements to minimal GeoJSON-like feature dicts."""
    features = []
    for el in elements:
        el_type = el.get("type")
        tags = el.get("tags", {})
        access_cat = classify(tags)

        # Ways have geometry as list of {lat, lon}
        if el_type == "way":
            geom = el.get("geometry", [])
            if len(geom) < 3:
                continue
            coords = [[pt["lon"], pt["lat"]] for pt in geom]
            # Close ring if not closed
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords],
                },
                "properties": {
                    "osm_id": el.get("id"),
                    "osm_type": "way",
                    "access_category": access_cat,
                    **{k: v for k, v in tags.items()},
                },
            })

        # Relations may have members with geometry
        elif el_type == "relation":
            members = el.get("members", [])
            outer_rings = []
            for member in members:
                if member.get("role") == "outer" and member.get("type") == "way":
                    geom = member.get("geometry", [])
                    if len(geom) < 3:
                        continue
                    coords = [[pt["lon"], pt["lat"]] for pt in geom]
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    outer_rings.append(coords)
            if not outer_rings:
                continue
            # Use first outer ring as a simple polygon
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [outer_rings[0]],
                },
                "properties": {
                    "osm_id": el.get("id"),
                    "osm_type": "relation",
                    "access_category": access_cat,
                    **{k: v for k, v in tags.items()},
                },
            })

    return features


def fetch_overpass(query: str, retries: int = 3) -> dict:
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        headers={
            "User-Agent": "nearest-gravhoj/0.1 (+local build)",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    for attempt in range(1, retries + 1):
        try:
            print(f"  Querying Overpass API (attempt {attempt})...", flush=True)
            with urllib.request.urlopen(req, timeout=360) as resp:
                return json.load(resp)
        except urllib.error.URLError as exc:
            if attempt == retries:
                raise
            print(f"  Failed: {exc}. Retrying in 10s...")
            time.sleep(10)
    raise RuntimeError("Overpass fetch failed after retries")


def main() -> int:
    print(f"Fetching Danish forest and nature areas from Overpass API...")
    print(f"Bounding box: {DK_BBOX}")
    print("This may take 1-3 minutes for all of Denmark...", flush=True)

    try:
        payload = fetch_overpass(OVERPASS_QUERY)
    except urllib.error.URLError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        return 1

    elements = payload.get("elements", [])
    print(f"  Got {len(elements)} OSM elements. Converting to GeoJSON...")

    features = overpass_to_geojson(elements)

    # Count by category
    from collections import Counter
    cats = Counter(f["properties"]["access_category"] for f in features)
    print(f"  always:  {cats.get('always', 0)}")
    print(f"  daylight:{cats.get('daylight', 0)}")

    result = {
        "source": "OpenStreetMap / Overpass API",
        "type": "adgang_dk",
        "feature_count": len(features),
        "crs": "EPSG:4326",
        "features": features,
    }

    ADGANG_PATH.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(f"Wrote {len(features)} access polygons to {ADGANG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
