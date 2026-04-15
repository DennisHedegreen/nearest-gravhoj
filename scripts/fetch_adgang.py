#!/usr/bin/env python3
"""
Fetch the Danish Adgangskort (public access polygons) from Miljøministeriets WFS.
Saves a local GeoJSON cache for use in the access join step.

WFS endpoint: https://wfs.friluftsliv.dk/geoserver/ows
This is the same service that powers friluftsliv.dk (Miljøministeriet).

Access categories produced:
  'always'   - always publicly accessible (state forests, beaches, heaths, etc.)
  'daylight' - accessible sunrise to sunset (private forests, §25 naturbeskyttelsesloven)
  'unknown'  - no polygon match found

If the WFS endpoint or layer name needs updating, run with --capabilities to list
available layers:
  python3 scripts/fetch_adgang.py --capabilities
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

WFS_BASE = "https://wfs.friluftsliv.dk/geoserver/ows"

# Layer name on the friluftsliv WFS.
# Run with --capabilities if this needs to be verified.
LAYER_NAME = "friluftsliv:adgangsregler"

ROOT = Path(__file__).resolve().parents[1]
ADGANG_PATH = ROOT / "data" / "adgang.raw.geojson"

PAGE_SIZE = 1000


def get_capabilities() -> None:
    url = (
        f"{WFS_BASE}?service=WFS&version=1.0.0&request=GetCapabilities"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "nearest-gravhoj/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode()
    # Print layer names only
    import re
    names = re.findall(r"<Name>([^<]+)</Name>", content)
    print("Available layers:")
    for name in names:
        print(f"  {name}")


def fetch_page(start_index: int) -> dict:
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": LAYER_NAME,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "maxFeatures": PAGE_SIZE,
        "startIndex": start_index,
    }
    url = f"{WFS_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nearest-gravhoj/0.1 (+local build)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def fetch_all() -> list:
    features = []
    start = 0
    while True:
        print(f"  Fetching page starting at {start}...", end=" ", flush=True)
        payload = fetch_page(start)
        page = payload.get("features", [])
        print(f"{len(page)} features")
        features.extend(page)
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE
    return features


def main(argv: list[str]) -> int:
    if "--capabilities" in argv:
        get_capabilities()
        return 0

    print(f"Fetching Adgangskort from {WFS_BASE} ...")
    try:
        features = fetch_all()
    except urllib.error.URLError as exc:
        print(f"Failed to fetch Adgangskort: {exc}", file=sys.stderr)
        print(
            "If the endpoint is wrong, run with --capabilities to list available layers.",
            file=sys.stderr,
        )
        return 1

    payload = {
        "source": "Adgangskort — Miljøministeriet / friluftsliv.dk",
        "type": "adgangsregler",
        "feature_count": len(features),
        "crs": "EPSG:4326",
        "features": features,
    }

    ADGANG_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(f"Wrote {len(features)} access polygons to {ADGANG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
