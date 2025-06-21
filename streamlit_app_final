# streamlit_app_final.py
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🏆 UEFA Club Match Checker (2025–26)")

# 1. URLs of the three Wikipedia club lists
URLS = {
    "UCL":   "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Champions_League_teams",
    "UEL":   "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League_teams",
    "UECL":  "https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Conference_League_teams",
}

def fetch_clubs_from_wiki(url, competition):
    """Scrape the Wikipedia page, return a list of dicts with name, country, stage."""
    tables = pd.read_html(url, flavor="bs4")
    clubs = []
    for df in tables:
        # look for a column that contains "Team" or "Club"
        for col in df.columns:
            if "Team" in col or "Club" in col:
                name_col = col
                break
        else:
            continue

        # stage inference: if table has “Group stage” in title or header
        stage = "Group" if "Group stage" in df.to_string() else "Qualifiers"
        for _, row in df.iterrows():
            name = row[name_col]
            if isinstance(name, str):
                clubs.append({
                    "name": name.strip(),
                    "country": row.get("Country", row.get("Nation", "")).strip(),
                    "competition": competition,
                    "stage": stage,
                    # we’ll fill crest below
                    "crest": None
                })
    return clubs

# 2. Build the full list
all_clubs = []
for comp, url in URLS.items():
    all_clubs += fetch_clubs_from_wiki(url, comp)

# 3. (Optional) Map club → crest URL via a small lookup dict.
#    For demo, we'll leave crest=None so dropdown shows text only,
#    or you can supply your own crest lookup here:
CREST_LOOKUP = {
    # "Manchester City": "https://…svg",
    # … paste any known crest URLs here …
}

for c in all_clubs:
    c["crest"] = CREST_LOOKUP.get(c["name"], None)

# 4. Exclusions & logic
EXCLUSIONS = {("KOS","SRB"),("ARM","AZE"),("BLR","UKR"),("GIB","ESP"),("ISR","GZA"),("UKR","RUS")}
def can_meet(a, b):
    if a["country"] == b["country"]:
        return False, "⚠️ Same country → only in knockout"
    pair = (a["country"], b["country"])
    if pair in EXCLUSIONS or pair[::-1] in EXCLUSIONS:
        return False, "🚫 Geopolitical block"
    if a["stage"]=="Group" and b["stage"]=="Group":
        return True, "✅ After group phase"
    return True, "✅ They can meet"

# 5. UI: side‑by‑side selectors
names = sorted({c["name"] for c in all_clubs})
col1, col2 = st.columns([1,1], gap="small")

with col1:
    sel1 = st.selectbox("Club A", names, key="A")
    club1 = next(c for c in all_clubs if c["name"] == sel1)

with col2:
    sel2 = st.selectbox("Club B", names, index=1, key="B")
    club2 = next(c for c in all_clubs if c["name"] == sel2)

# 6. Display crests (if available)
c1, c2 = club1["crest"], club2["crest"]
r1, r2 = st.columns(2)
with r1:
    if c1:
        st.image(c1, width=80)
with r2:
    if c2:
        st.image(c2, width=80)

# 7. Compute & show result
ok, msg = (None, "Select two different clubs") if sel1==sel2 else can_meet(club1, club2)
color = "#d4edda" if ok else "#f8d7da" if ok==False else "#fff3cd"
textc = "#155724" if ok else "#721c24" if ok==False else "#856404"

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="
  max-width:600px;margin:0 auto;
  background:{color};color:{textc};
  padding:1em;border-radius:8px;
  font-size:18px;text-align:center;">
  <strong>{sel1}</strong> vs <strong>{sel2}</strong><br>{msg}
</div>
""", unsafe_allow_html=True)
