#!/usr/bin/env python3
"""
Join gravhøj points against Adgangskort polygons and write the slim JSON
with an 'access' field added to each feature.

Access values:
  'always'   - always publicly accessible
  'daylight' - accessible sunrise to sunset (private forests)
  'unknown'  - no polygon match (likely private agricultural land)

Requires: shapely >= 2.0
Install: pip install -r requirements.txt

Usage:
  python3 scripts/join_access.py

Input:
  data/rundhoje.raw.geojson   (from fetch_rundhoje.py)
  data/adgang.raw.geojson     (from fetch_adgang.py)

Output:
  data/rundhoje.min.json      (replaces the current slim file)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from shapely.geometry import Point, shape
    from shapely.strtree import STRtree
except ImportError:
    print("shapely is required. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
GRAVHOJ_PATH = ROOT / "data" / "rundhoje.raw.geojson"
ADGANG_PATH = ROOT / "data" / "adgang.raw.geojson"
SLIM_PATH = ROOT / "data" / "rundhoje.min.json"

# Map WFS field values to our three categories.
# Adjust these if the actual field name or values differ from the WFS.
# Run fetch_adgang.py and inspect a few features to verify.
def classify(props: dict) -> str:
    # access_category is set by fetch_adgang.py during conversion
    return props.get("access_category", "unknown")


def build_spatial_index(adgang_features: list) -> tuple[STRtree, list]:
    geometries = []
    for feat in adgang_features:
        try:
            geometries.append(shape(feat["geometry"]))
        except Exception:
            geometries.append(None)
    valid = [(g, adgang_features[i]) for i, g in enumerate(geometries) if g is not None]
    tree = STRtree([g for g, _ in valid])
    return tree, valid


def lookup_access(point: Point, tree: STRtree, valid: list) -> str:
    candidate_indices = tree.query(point)
    for idx in candidate_indices:
        geom, feat = valid[idx]
        if geom.contains(point):
            return classify(feat.get("properties", {}))
    return "unknown"


def main() -> int:
    if not GRAVHOJ_PATH.exists():
        print(f"Missing {GRAVHOJ_PATH} — run fetch_rundhoje.py first", file=sys.stderr)
        return 1
    if not ADGANG_PATH.exists():
        print(f"Missing {ADGANG_PATH} — run fetch_adgang.py first", file=sys.stderr)
        return 1

    print("Loading gravhøj data...")
    with open(GRAVHOJ_PATH, encoding="utf-8") as f:
        gravhoj_payload = json.load(f)
    gravhoj_features = gravhoj_payload.get("features", [])

    print("Loading Adgangskort data...")
    with open(ADGANG_PATH, encoding="utf-8") as f:
        adgang_payload = json.load(f)
    adgang_features = adgang_payload.get("features", [])

    print(f"Building spatial index over {len(adgang_features)} access polygons...")
    tree, valid = build_spatial_index(adgang_features)

    print(f"Joining {len(gravhoj_features)} gravhøje against access index...")
    slim_features = []
    counts = {"always": 0, "daylight": 0, "unknown": 0}

    for i, feat in enumerate(gravhoj_features):
        if i % 2000 == 0:
            print(f"  {i}/{len(gravhoj_features)}")

        coords = feat.get("geometry", {}).get("coordinates")
        props = feat.get("properties", {})
        if not coords or len(coords) != 2:
            continue

        lon, lat = float(coords[0]), float(coords[1])
        point = Point(lon, lat)
        access = lookup_access(point, tree, valid)
        counts[access] += 1

        slim_features.append(
            {
                "id": props.get("systemnr"),
                "dating": props.get("datering") or "",
                "stednr": props.get("stednr") or "",
                "frednr": props.get("frednr") or "",
                "lon": round(lon, 7),
                "lat": round(lat, 7),
                "access": access,
            }
        )

    result = {
        "source": "Fund og Fortidsminder WFS + Adgangskort",
        "type": "Rundhøj",
        "feature_count": len(slim_features),
        "crs": "EPSG:4326",
        "features": slim_features,
    }

    SLIM_PATH.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(f"\nWrote {len(slim_features)} features to {SLIM_PATH}")
    print(f"  always:  {counts['always']}")
    print(f"  daylight:{counts['daylight']}")
    print(f"  unknown: {counts['unknown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
