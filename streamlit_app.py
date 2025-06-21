
import streamlit as st

# --- UEFA 2025–26 Clubs (shortened for example; extend in practice)
qualified_clubs = [
    {"name": "Fiorentina", "country": "ITA", "competition": "UECL", "stage": "League"},
    {"name": "Nottingham Forest", "country": "ENG", "competition": "UECL", "stage": "League"},
    {"name": "Rayo Vallecano", "country": "ESP", "competition": "UECL", "stage": "League"},
    {"name": "Mainz 05", "country": "GER", "competition": "UECL", "stage": "League"},
    {"name": "Strasbourg", "country": "FRA", "competition": "UECL", "stage": "League"},
    {"name": "AZ Alkmaar", "country": "NLD", "competition": "UECL", "stage": "League"},
    {"name": "Santa Clara", "country": "PRT", "competition": "UECL", "stage": "League"},
    {"name": "Sparta Praha", "country": "CZE", "competition": "UECL", "stage": "League"},
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

# --- Streamlit UI
st.title("🏆 UEFA Club Match Checker")
st.markdown("Check if two UEFA clubs can meet in 2025–26 European competitions")

club_names = [club["name"] for club in qualified_clubs]
club1_name = st.selectbox("Select Club 1", club_names)
club2_name = st.selectbox("Select Club 2", club_names, index=1)

club1 = next(c for c in qualified_clubs if c["name"] == club1_name)
club2 = next(c for c in qualified_clubs if c["name"] == club2_name)

if club1_name == club2_name:
    st.warning("Please select two different clubs.")
else:
    result = can_meet(club1, club2)
    st.success(f"{club1_name} vs {club2_name}: {result}")
