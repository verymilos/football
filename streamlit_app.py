import streamlit as st
import json

# Map short stage codes to full names
stage_names = {
    "q1": "First Qualifying Round",
    "q2": "Second Qualifying Round",
    "q3": "Third Qualifying Round",
    "playoff": "Playoff Round",
    "gs": "Group Stage",
    "group stage": "Group Stage",
    "r32": "Round of 32",
    "r16": "Round of 16",
    "quarterfinal": "Quarterfinals",
    "semifinal": "Semifinals",
    "final": "Final",
}

def pretty_stage(stage_raw):
    if not stage_raw:
        return "N/A"
    s = stage_raw.strip().lower()
    if s in stage_names:
        return stage_names[s]
    for key, val in stage_names.items():
        if key in s:
            return val
    return stage_raw.title()

# Competition logos URLs (replace with your own URLs or public URLs)
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/UEFA_Champions_League_logo_2.svg/120px-UEFA_Champions_League_logo_2.svg.png",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6e/UEFA_Europa_League_logo_2021.svg/120px-UEFA_Europa_League_logo_2021.svg.png",
    "UECL": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/UEFA_Conference_League_logo.svg/120px-UEFA_Conference_League_logo.svg.png",
}

# Load clubs data from JSON
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Sort clubs alphabetically by club name
sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

# Helper to get club info by name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

# UI layout
col1, col2 = st.columns(2)

with col1:
    st.image(competition_logos.get("UCL"), width=120, caption="UEFA Champions League")
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = get_club_info(selected_club_1)
    if club1:
        st.markdown(f"**Entry Stage:** {pretty_stage(club1.get('entry_stage'))}")

with col2:
    st.image(competition_logos.get("UEL"), width=120, caption="UEFA Europa League")
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")
    club2 = get_club_info(selected_club_2)
    if club2:
        st.markdown(f"**Entry Stage:** {pretty_stage(club2.get('entry_stage'))}")

# Your existing logic for can_meet() here (not repeated for brevity)...

# Logic to determine if clubs can meet
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, "They can only meet after the Group Stage due to same-country restriction."

    if "Russia" in [club1["country"], club2["country"]]:
        return False, "Russian clubs are suspended from UEFA competitions."

    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan")
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"{c1} and {c2} clubs are not allowed to meet in UEFA competitions."

    return True, "These clubs can potentially meet in UEFA competitions."

can_play, message = can_meet(club1, club2)

# Show result with color feedback
st.markdown("### Result")
result_color = "green" if can_play else "red"
st.markdown(f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.2em;'>{message}</div>", unsafe_allow_html=True)
