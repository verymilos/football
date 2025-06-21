
import streamlit as st

# Sample club list with crests (extend with full dataset)
qualified_clubs = [
    {"name": "Fiorentina", "country": "ITA", "competition": "UECL", "stage": "League",
     "crest": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5b/ACF_Fiorentina_2.svg/1200px-ACF_Fiorentina_2.svg.png"},
    {"name": "Nottingham Forest", "country": "ENG", "competition": "UECL", "stage": "League",
     "crest": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/Nottingham_Forest_F.C._logo.svg/1200px-Nottingham_Forest_F.C._logo.svg.png"},
    {"name": "Rayo Vallecano", "country": "ESP", "competition": "UECL", "stage": "League",
     "crest": "https://upload.wikimedia.org/wikipedia/en/thumb/5/51/Rayo_Vallecano_logo.svg/1200px-Rayo_Vallecano_logo.svg.png"},
    {"name": "Mainz 05", "country": "GER", "competition": "UECL", "stage": "League",
     "crest": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d5/1._FSV_Mainz_05_Logo.svg/1200px-1._FSV_Mainz_05_Logo.svg.png"},
    {"name": "Strasbourg", "country": "FRA", "competition": "UECL", "stage": "League",
     "crest": "https://upload.wikimedia.org/wikipedia/en/thumb/6/65/Racing_Club_de_Strasbourg_logo.svg/1200px-Racing_Club_de_Strasbourg_logo.svg.png"},
]

exclusions = {
    ("KOS", "SRB"),
    ("ARM", "AZE"),
    ("UKR", "RUS"),
}

def can_meet(club1, club2):
    if club1["country"] == club2["country"]:
        return "⚠️ Same country: Can only meet in knockout rounds"
    countries = {club1["country"], club2["country"]}
    if tuple(countries) in exclusions or tuple(reversed(tuple(countries))) in exclusions:
        return "🚫 Cannot meet due to geopolitical restrictions"
    if club1["stage"] == "League" and club2["stage"] == "League":
        return "✅ Can meet after League Phase (not in group draw)"
    return "✅ They can meet"

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🏆 UEFA Club Match Checker")

club_names = [club["name"] for club in qualified_clubs]

col1, col2 = st.columns(2)

with col1:
    club1_name = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = next(c for c in qualified_clubs if c["name"] == club1_name)
    st.image(club1["crest"], width=100)

with col2:
    club2_name = st.selectbox("Select Club 2", club_names, index=1, key="club2")
    club2 = next(c for c in qualified_clubs if c["name"] == club2_name)
    st.image(club2["crest"], width=100)

if club1_name != club2_name:
    result = can_meet(club1, club2)
    st.markdown(
        f"<div style='text-align: center; font-size: 20px; padding: 1em; background-color: #f0f2f6; border-radius: 10px;'>"
        f"<b>{club1_name}</b> vs <b>{club2_name}</b>:<br>{result}</div>",
        unsafe_allow_html=True
    )
else:
    st.warning("Please select two different clubs.")
