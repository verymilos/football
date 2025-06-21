
import streamlit as st
import json

# Load clubs data from JSON file
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()
club_names = sorted([club["name"] for club in clubs_data])

# Create mapping from name to full club data
club_lookup = {club["name"]: club for club in clubs_data}

# UI Layout
st.set_page_config(page_title="UEFA Club Match Possibility", layout="wide")
st.markdown("<h1 style='text-align: center;'>🔍 UEFA Club Match Checker 2025/26</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    club1_name = st.selectbox("Choose Club 1", club_names, key="club1")

with col2:
    club2_name = st.selectbox("Choose Club 2", club_names, key="club2")

# Club details
club1 = club_lookup[club1_name]
club2 = club_lookup[club2_name]

def can_meet(club1, club2):
    if club1["name"] == club2["name"]:
        return False, "Same club selected."
    if "Russia" in (club1["country"], club2["country"]):
        return False, "Russian clubs are suspended from UEFA competitions."
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Kosovo", "Serbia"),
        ("Armenia", "Azerbaijan"),
        ("Azerbaijan", "Armenia")
    ]
    if (club1["country"], club2["country"]) in blocked_pairs:
        return False, f"Clubs from {club1['country']} and {club2['country']} cannot meet due to geopolitical restrictions."
    if club1["country"] == club2["country"]:
        if club1["stage"] == "Group" and club2["stage"] == "Group":
            return False, "Clubs from the same country cannot be drawn together in the group stage."
    return True, f"{club1['name']} and {club2['name']} could meet in a later stage of UEFA competition."

can_meet_result, reason = can_meet(club1, club2)

# Result Box
result_color = "green" if can_meet_result else "red"
result_html = f"""
<div style='margin-top:20px;padding:20px;background-color:{result_color};color:white;border-radius:10px;text-align:center;font-size:20px'>
    {reason}
</div>
"""
st.markdown(result_html, unsafe_allow_html=True)
