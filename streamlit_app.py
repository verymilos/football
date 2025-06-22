import streamlit as st
import json

# Mapping for full stage names
stage_full_names = {
    "Q1": "First Qualifying Round",
    "Q2": "Second Qualifying Round",
    "Q3": "Third Qualifying Round",
    "PO": "Play-off Round",
    "GS": "Group Stage",
    "R32": "Round of 32",
    "R16": "Round of 16",
    "QF": "Quarter-finals",
    "SF": "Semi-finals",
    "F": "Final",
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

# UI - Club selection dropdowns
col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")

# Retrieve full club info by club name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

# Display club crest and entry stage info side-by-side
def show_club_info(club):
    cols = st.columns([1, 3])
    with cols[0]:
        if club.get("crest_url"):
            st.image(club["crest_url"], width=120)
    with cols[1]:
        entry_stage_full = stage_full_names.get(club.get("entry_stage", ""), club.get("entry_stage", "Unknown Stage"))
        st.markdown(f"**Entry Stage:** {entry_stage_full}")
        st.markdown(f"**Competition:** {club.get('competition', 'Unknown')}")

st.markdown("### Club Info")

info_col1, info_col2 = st.columns(2)
with info_col1:
    show_club_info(club1)
with info_col2:
    show_club_info(club2)

# The main can_meet function with refined messages
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Same country clubs in same competition can't meet before knockouts
    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, (
            f"Both clubs are from {club1['country']} and play in the {club1['competition']}.\n"
            "They cannot meet before the knockout stages due to UEFA restrictions."
        )

    # Example: Russian clubs suspended (customize or remove as needed)
    if "Russia" in [club1["country"], club2["country"]]:
        return False, "Russian clubs are currently suspended from UEFA competitions."

    # Specific blocked country pairs (simplified example)
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan"),
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"{c1} and {c2} clubs are not allowed to meet in UEFA competitions."

    # Helper to detect if a club can drop from one competition to another based on entry stage
    def competition_transfer_path(club):
        comp = club["competition"]
        stage = club.get("entry_stage", "")
        if comp == "UCL" and stage in ["Q1", "Q2", "Q3", "PO"]:
            return "UCL → UEL"
        if comp == "UEL" and stage in ["Q1", "Q2", "Q3", "PO"]:
            return "UEL → UECL"
        return None

    transfer1 = competition_transfer_path(club1)
    transfer2 = competition_transfer_path(club2)

    messages = []

    if transfer1:
        messages.append(
            f"{club1['club']} starts in {club1['competition']} ({stage_full_names.get(club1['entry_stage'], club1['entry_stage'])}) "
            f"and can drop to {transfer1.split('→')[1]} stages, possibly facing {club2['club']}."
        )

    if transfer2:
        messages.append(
            f"{club2['club']} starts in {club2['competition']} ({stage_full_names.get(club2['entry_stage'], club2['entry_stage'])}) "
            f"and can drop to {transfer2.split('→')[1]} stages, possibly facing {club1['club']}."
        )

    if messages:
        return True, " ".join(messages)

    # Default fallback message
    return True, "These clubs can potentially meet in UEFA competitions."

# Run logic and show result
can_play, message = can_meet(club1, club2)

st.markdown("### Result")
result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.1em;'>"
    f"{message}"
    "</div>",
    unsafe_allow_html=True
)
