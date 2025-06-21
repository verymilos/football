import requests, json, pandas as pd
from bs4 import BeautifulSoup

URLS = {
    "UCL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Champions_League",
    "UEL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League",
    "UECL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_Conference_League",
}

def fetch(url, competition):
    tables = pd.read_html(url, flavor="bs4")
    clubs = []
    for table in tables:
        columns = list(table.columns)
        if not any("Team" in str(col) or "Club" in str(col) for col in columns):
            continue
        for _, row in table.iterrows():
            name = row.get("Team") or row.get("Club") or row.get(columns[0])
            country = row.get("Country") or row.get("Nation") or ""
            if isinstance(name, str) and name.strip():
                clubs.append({
                    "name": name.strip(),
                    "country": country.strip() if isinstance(country, str) else "",
                    "competition": competition,
                    "stage": "Group" if "Group" in str(table.columns) else "Qualifying",
                    "crest": None
                })
    return clubs

all_clubs = []
for comp, url in URLS.items():
    try:
        all_clubs.extend(fetch(url, comp))
    except Exception as e:
        print(f"Error processing {comp}: {e}")

with open("clubs.json", "w", encoding="utf-8") as f:
    json.dump(all_clubs, f, indent=2, ensure_ascii=False)

print(f"✅ clubs.json created with {len(all_clubs)} clubs")
