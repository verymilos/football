#!/usr/bin/env python3
import requests, json, pandas as pd
from io import StringIO

# Source URLs for fullscreen official club lists
URLS = {
    "UCL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Champions_League_teams",
    "UEL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League_teams",
    "UECL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Conference_League_teams",
}

def fetch(url, comp):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    tables = pd.read_html(StringIO(resp.text), flavor="bs4")
    result = []
    for df in tables:
        name = next((c for c in df.columns if "Team" in c or "Club" in c), None)
        if not name: continue
        stage = "Group" if "Group stage" in df.to_string() else "Qualifying"
        country = next((c for c in df.columns if c in ("Country","Nation")), None)
        for _, row in df.iterrows():
            nm = row[name] if pd.notna(row[name]) else None
            if nm:
                result.append({
                    "name": nm.strip(),
                    "country": (row[country] if country else "").strip(),
                    "competition": comp,
                    "stage": stage,
                    "crest": None
                })
    return result

all_clubs = []
for comp, url in URLS.items():
    all_clubs += fetch(url, comp)

with open("clubs.json", "w", encoding="utf-8") as f:
    json.dump(all_clubs, f, ensure_ascii=False, indent=2)

print(f"✅ Generated clubs.json with {len(all_clubs)} clubs")
