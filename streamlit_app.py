import streamlit as st
import json

# Load clubs data from JSON
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Sort clubs alphabetically by club name
sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

# Full stage names mapping
stage_full_names = {
    "Q1": "First Qualifying Round",
    "Q2": "Second Qualifying Round",
    "Q3": "Third Qualifying Round",
    "PO": "Play-Off Round",
    "GS": "Group Stage",
    "R16": "Round of 16",
    "QF": "Quarter-Finals",
    "SF": "Semi-Finals",
    "F": "Final"
}

# Competition logos (PNG direct URLs)
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/1/11/UEFA_Champions_League_logo_2.svg.png",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/6/63/UEFA_Europa_League_logo_2021.png",
    "UECL": "https://upload.wikimedia.org/wikipedia/en/4/49/UEFA_Conference_League_logo.png"
}

# Helper to get club info by club name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

# Show club crest + competition logo + entry stage (full name) above dropdown
def show_club_info(club):
    if not club:
        st.write("Club info not found")
        return
    cols = st.columns([1, 0.75])  # crest and competition logo side by side
    with cols[0]:
        crest_url = club.get("crest_url")
        if crest_url:
            st.image(crest_url, width=120)
else:
    st.write("No crest available")
    with cols[1]:
        comp_logo = competition_logos.get(club.get("competition"))
        if comp_logo:
            st.image(comp_logo, width=90)
    entry_stage_full = stage_full_names.get(club.get("entry_stage"), club.get("entry_stage"))
    st.markdown(f"**Entry Stage:** {entry_stage_full}")

# Layout: two columns with dropdowns
col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = get_club_info(selected_club_1)
    show_club_info(club1)

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")
    club2 = get_club_info(selected_club_2)
    show_club_info(club2)

# Example logic for match possibility (basic placeholder, customize as needed)
def can_meet(c1, c2):
    if not c1 or not c2 or c1 == c2:
        return False, "Invalid club selection."
    if c1["country"] == c2["country"] and c1["competition"] == c2["competition"]:
        return True, "Same country clubs can meet only after the Group Stage."
    # Add your advanced logic here
    return True, "These clubs can potentially meet."

can_play, message = can_meet(club1, club2)

st.markdown("### Result")
result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.2em;'>"
    f"{message}"
    "</div>",
    unsafe_allow_html=True,
)
