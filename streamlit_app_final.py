import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(layout="wide")
st.title("🏆 UEFA Club Match Checker (2025–26)")

# 1. Wikipedia URLs
URLS = {
    "UCL":  "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Champions_League_teams",
    "UEL":  "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League_teams",
    "UECL": "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Conference_League_teams",
}

# 2. Fetch + parse tables
def fetch_clubs_from_wiki(url, competition):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; UEFA Club Checker/1.0)"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    html = resp.text
    tables = pd.read_html(StringIO(html), flavor="bs4")
    clubs = []
    for df in tables:
        # find the column that holds the team name
        name_col = next((c for c in df.columns if "Team" in c or "Club" in c), None)
        if not name_col:
            continue
        # determine stage
        stage = "Group" if "Group stage" in df.to_string() else "Qualifiers"
        for _, row in df.iterrows():
            name = row[name_col]
            if isinstance(name, str) and name.strip():
                clubs.append({
                    "name": name.strip(),
                    "country": row.get("Country", row.get("Nation", "")).strip(),
                    "competition": competition,
                    "stage": stage,
                    "crest": None
                })
    return clubs

# 3. Build full list
all_clubs = []
for comp, url in URLS.items():
    all_clubs += fetch_clubs_from_wiki(url, comp)

# 4. (Optional) Crest lookup
CREST_LOOKUP = {
    # example: "Manchester City": "https://...svg",
}
for c in all_clubs:
    c["crest"] = CREST_LOOKUP.get(c["name"], None)

# 5. Exclusions & can_meet
EXCLUSIONS = {
    ("KOS","SRB"),("ARM","AZE"),("BLR","UKR"),
    ("GIB","ESP"),("ISR","GZA"),("UKR","RUS")
}
def can_meet(a, b):
    if a["country"] == b["country"]:
        return False, "⚠️ Same country → only in knockout"
    pair = (a["country"], b["country"])
    if pair in EXCLUSIONS or pair[::-1] in EXCLUSIONS:
        return False, "🚫 Geopolitical block"
    if a["stage"]=="Group" and b["stage"]=="Group":
        return True, "✅ They can meet after group phase"
    return True, "✅ They can meet"

# 6. UI selectors side by side
names = sorted({c["name"] for c in all_clubs})
col1, col2 = st.columns([1,1], gap="small")
with col1:
    sel1 = st.selectbox("Club A", names, key="A")
    club1 = next(c for c in all_clubs if c["name"] == sel1)
with col2:
    sel2 = st.selectbox("Club B", names, index=1, key="B")
    club2 = next(c for c in all_clubs if c["name"] == sel2)

# 7. Display crests (if available)
c1, c2 = club1["crest"], club2["crest"]
r1, r2 = st.columns(2)
with r1:
    if c1:
        st.image(c1, width=80)
with r2:
    if c2:
        st.image(c2, width=80)

# 8. Compute & show result
ok, msg = (None, "Select two different clubs") if sel1==sel2 else can_meet(club1, club2)
color = "#d4edda" if ok else "#f8d7da" if ok==False else "#fff3cd"
textc = "#155724" if ok else "#721c24" if ok==False else "#856404"
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="
  max-width:600px; margin:0 auto;
  background:{color}; color:{textc};
  padding:1em; border-radius:8px;
  font-size:18px; text-align:center;">
  <strong>{sel1}</strong> vs <strong>{sel2}</strong><br>{msg}
</div>
""", unsafe_allow_html=True)
