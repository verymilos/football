#!/usr/bin/env python3
import requests
import pandas as pd
import json
from io import StringIO

# Wikipedia URLs for 2025–26 competitions (update when needed)
URLS = {
    "UCL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Champions_League",
    "UEL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League",
    "UECL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Conference_League",
}

def fetch_clubs(url, comp):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html = response.text

    tables = pd.read_html(StringIO(html), flavor="bs4")
    clubs = []

    for df in tables:
        name_col = next((c for c in df.columns if "Team" in c or "Club" in c), None)
        if not name_col:
            continue
        stage = "Group" if "Group stage" in df.to_string() else "Qualifiers"
        country_col = next((c for c in df.columns if "Country" in c or "Nation" in c), None)
        for _, row in df.iterrows():
            name = row[name_col]
            if isinstance(name, str) and name.strip():
                country = row.get(country_col, "")
                clubs.append({
                    "name": name.strip(),
                    "country": country.strip() if isinstance(country, str) else "",
                    "competition": comp,
                    "stage": stage,
                    "crest": None  # You can add URLs for crests later
                })
    return clubs

def main():
    all_clubs = []
    for comp, url in URLS.items():
        all_clubs.extend(fetch_clubs(url, comp))
    with open("clubs.json", "w", encoding="utf-8") as f:
        json.dump(all_clubs, f, indent=2, ensure_ascii=False)
    print(f"✅ Fetched and saved {len(all_clubs)} clubs into clubs.json")

if __name__ == "__main__":
    main()
