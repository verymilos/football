import streamlit as st
import json

# Mapping of short stage codes to full names
stage_full_names = {
    "Q1": "First Qualifying Round",
    "Q2": "Second Qualifying Round",
    "Q3": "Third Qualifying Round",
    "PO": "Playoffs",
    "GS": "Group Stage",
    "R32": "Round of 32",
    "R16": "Round of 16",
    "QF": "Quarter-finals",
    "SF": "Semi-finals",
    "F": "Final"
}

# Competition logos from Wikimedia Commons
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/UEFA_Champions_League_logo_2.svg/120px-UEFA_Champions_League_logo_2.svg.png",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/UEFA_Europa_League_logo.svg/120px-UEFA_Europa_League_logo.svg.png",
    "UECL": "https://upload.wikimedia.org/wikipedia/en/thumb/6/65/UEFA_Europa_Conference_League_logo.svg/120px-UEFA_Europa_Conference_League_logo.svg.png"
}

@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Sort clubs alphabetically by "club" key
sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

def show_club_info(club):
    cols = st.columns([1, 1, 3])
    with cols[0]:
        if club.get("crest_url"):
            st.image(club["crest_url"], width=120)
    with cols[1]:
        comp_logo_url = competition_logos.get(club.get("competition"), None)
        if comp_logo_url:
            st.image(comp_logo_url, width=90)  # 75% of crest width (120)
    with cols[2]:
        entry_stage = club.get("entry_stage", "Unknown")
        entry_stage_full = stage_full_names.get(entry_stage, entry_stage)
        st.markdown(f"**Entry Stage:** {entry_stage_full}")
        st.markdown(f"**Competition:** {club.get('competition', 'Unknown')}")

# Club selection UI
col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")

def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

show_club_info(club1)
show_club_info(club2)

# Simplified example meeting logic (expand as needed)
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Same country restriction for same competition
    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, "They can only meet after the Group Stage due to same-country restriction."

    # Suspended Russian clubs example
    if "Russia" in [club1["country"], club2["country"]]:
        return False, "Russian clubs are suspended from UEFA competitions."

    # Serbia-Kosovo and Armenia-Azerbaijan exclusion example
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan")
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"{c1} and {c2} clubs are not allowed to meet in UEFA competitions."

    # Additional refined logic should be implemented here!

    return True, "These clubs can potentially meet in UEFA competitions depending on competition and stage."

can_play, message = can_meet(club1, club2)

# Display result with colored background
result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.2em;'>"
    f"{message}"
    "</div>",
    unsafe_allow_html=True,
)
