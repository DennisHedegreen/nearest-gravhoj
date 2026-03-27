#!/usr/bin/env python3
"""
Fetch a filtered Rundhøj extract from the official Fund og Fortidsminder WFS
and write a slim local JSON file for the nearest-gravhoj app.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


WFS_BASE = "https://www.kulturarv.dk/ffgeoserver/public/wfs"
QUERY = {
    "service": "WFS",
    "version": "1.0.0",
    "request": "GetFeature",
    "typeName": "public:fundogfortidsminder_punkt_fredet",
    "outputFormat": "application/json",
    "srsName": "EPSG:4326",
    "CQL_FILTER": "anlaegstype = 'Rundhøj'",
}

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "rundhoje.raw.geojson"
SLIM_PATH = ROOT / "data" / "rundhoje.min.json"


def fetch_geojson() -> dict:
    url = f"{WFS_BASE}?{urllib.parse.urlencode(QUERY)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nearest-gravhoj/0.1 (+local build)",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def slim_features(payload: dict) -> dict:
    features = []
    for feature in payload.get("features", []):
        coords = feature.get("geometry", {}).get("coordinates")
        props = feature.get("properties", {})
        if not coords or len(coords) != 2:
            continue

        features.append(
            {
                "id": props.get("systemnr"),
                "dating": props.get("datering") or "",
                "stednr": props.get("stednr") or "",
                "frednr": props.get("frednr") or "",
                "lon": round(float(coords[0]), 7),
                "lat": round(float(coords[1]), 7),
            }
        )

    return {
        "source": "Fund og Fortidsminder WFS",
        "type": "Rundhøj",
        "feature_count": len(features),
        "crs": "EPSG:4326",
        "features": features,
    }


def main() -> int:
    try:
        payload = fetch_geojson()
    except urllib.error.URLError as exc:
        print(f"Failed to fetch official Rundhøj data: {exc}", file=sys.stderr)
        return 1

    RAW_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    slim = slim_features(payload)
    SLIM_PATH.write_text(
        json.dumps(slim, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(f"Wrote raw GeoJSON: {RAW_PATH}")
    print(f"Wrote slim JSON:  {SLIM_PATH}")
    print(f"Feature count:    {slim['feature_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
