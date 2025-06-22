import streamlit as st
import json

# Load clubs data
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Sort clubs by name
sorted_clubs = sorted(clubs_data, key=lambda c: c["club"])
club_names = [c["club"] for c in sorted_clubs]

# Competition logos URLs (make sure these URLs work for you)
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/UEFA_Champions_League_logo_2.svg/1200px-UEFA_Champions_League_logo_2.svg.png",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/UEFA_Europa_League_logo_2015.svg/1200px-UEFA_Europa_League_logo_2015.svg.png",
    "UECL": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2f/UEFA_Europa_Conference_League_logo.svg/1200px-UEFA_Europa_Conference_League_logo.svg.png",
}

# UI columns for selection
col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")

# Helper to get club data by name
def get_club_info(name):
    return next((c for c in clubs_data if c["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

# Function to show club crest, competition logo, and entry stage
def show_club_info(club):
    if not club:
        st.write("No club selected")
        return

    crest_url = club.get("crest_url")
    comp = club.get("competition")
    entry_stage = club.get("entry_stage", "Unknown stage")

    # Layout images side by side
    c1, c2 = st.columns([4, 3])

    with c1:
        if crest_url:
            st.image(crest_url, width=120)
        else:
            st.write("No crest available")

    with c2:
        if comp in competition_logos:
            # 75% width of crest (120 * 0.75 = 90)
            st.image(competition_logos[comp], width=90)
        else:
            st.write("No competition logo")

    st.markdown(f"Entry stage: **{entry_stage}**")

# Show club info side by side
info_col1, info_col2 = st.columns(2)

with info_col1:
    show_club_info(club1)

with info_col2:
    show_club_info(club2)

# Logic placeholder for meeting conditions
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Example: same country restriction in same competition
    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, "They can only meet after the group stage due to same-country restriction."

    # Add your detailed logic here...

    return True, "These clubs can potentially meet in UEFA competitions."

can_play, message = can_meet(club1, club2)

# Show result with colors
st.markdown("### Result")
color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {color}; color: white; text-align: center; font-weight: bold;'>"
    f"{message}</div>", unsafe_allow_html=True
)
