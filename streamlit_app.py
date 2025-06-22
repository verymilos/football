import streamlit as st
import json

# Load clubs data
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Sort clubs alphabetically
sorted_clubs = sorted(clubs_data, key=lambda c: c["club"])
club_names = [c["club"] for c in sorted_clubs]

# Competition logos URLs
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/UEFA_Champions_League_logo_2.svg/1200px-UEFA_Champions_League_logo_2.svg.png",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/UEFA_Europa_League_logo_2015.svg/1200px-UEFA_Europa_League_logo_2015.svg.png",
    "UECL": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2f/UEFA_Europa_Conference_League_logo.svg/1200px-UEFA_Europa_Conference_League_logo.svg.png",
}

# Mapping entry_stage codes to full English
stage_full_names = {
    "Q1": "First Qualifying Round",
    "Q2": "Second Qualifying Round",
    "Q3": "Third Qualifying Round",
    "PO": "Play-Off Round",
    "GS": "Group Stage",
    "R16": "Round of 16",
    "QF": "Quarter-Final",
    "SF": "Semi-Final",
    "F": "Final"
}

col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")

def get_club_info(name):
    return next((c for c in clubs_data if c["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

def show_club_info(club):
    if not club:
        st.write("No club selected")
        return

    crest_url = club.get("crest_url")
    comp = club.get("competition")
    entry_stage_code = club.get("entry_stage", "Unknown")
    entry_stage = stage_full_names.get(entry_stage_code, entry_stage_code)

    c1, c2 = st.columns([4, 3])
    with c1:
        if crest_url:
            st.image(crest_url, width=120)
        else:
            st.write("No crest available")
    with c2:
        if comp in competition_logos:
            st.image(competition_logos[comp], width=90)
        else:
            st.write("No competition logo")
    st.markdown(f"Entry stage: **{entry_stage}**")

info_col1, info_col2 = st.columns(2)

with info_col1:
    show_club_info(club1)
with info_col2:
    show_club_info(club2)


def can_meet(c1, c2):
    if not c1 or not c2 or c1 == c2:
        return False, "Invalid club selection."

    # Clubs in different competitions can only meet if one drops down to another competition (e.g. UCL Q2 losers go to UEL Q3)
    # Very simplified example:
    comp1, comp2 = c1["competition"], c2["competition"]
    stage1, stage2 = c1.get("entry_stage"), c2.get("entry_stage")
    country1, country2 = c1["country"], c2["country"]

    # If clubs are in different comps, only meet if path exists (simplified):
    # Example: UCL Q1/Q2 loser drops to UEL Q2/Q3
    ucl_to_uel = {
        "Q1": "Q1",
        "Q2": "Q2",
        "Q3": "PO",
        "PO": "GS"
    }
    if comp1 != comp2:
        # Check if club1 drops to club2's comp stage or vice versa
        if comp1 == "UCL" and comp2 == "UEL":
            if ucl_to_uel.get(stage1, "") == stage2:
                return True, f"{c1['club']} can meet {c2['club']} after dropping from UCL to UEL."
            else:
                return False, f"{c1['club']} and {c2['club']} unlikely to meet as competition paths don't align."
        if comp2 == "UCL" and comp1 == "UEL":
            if ucl_to_uel.get(stage2, "") == stage1:
                return True, f"{c2['club']} can meet {c1['club']} after dropping from UCL to UEL."
            else:
                return False, f"{c1['club']} and {c2['club']} unlikely to meet as competition paths don't align."

        # Similar logic can be added for UEL->UECL paths if needed

        return False, f"{c1['club']} and {c2['club']} compete in different competitions and unlikely to meet."

    # If same competition:

    # Same country clubs cannot meet in Group Stage
    if country1 == country2 and comp1 == comp2:
        if stage1 == "GS" or stage2 == "GS":
            return False, "Same-country clubs cannot meet in Group Stage."

    # Only meet if stages overlap logically - simplified:
    stages_order = ["Q1", "Q2", "Q3", "PO", "GS", "R16", "QF", "SF", "F"]
    if stage1 not in stages_order or stage2 not in stages_order:
        return False, "Unknown stages prevent meeting."

    idx1 = stages_order.index(stage1)
    idx2 = stages_order.index(stage2)

    if abs(idx1 - idx2) > 2:
        return False, "Clubs at very different stages unlikely to meet."

    # Exclusions example (Serbia vs Kosovo)
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan")
    ]
    if {country1, country2} in [set(pair) for pair in blocked_pairs]:
        return False, f"Clubs from {country1} and {country2} are not allowed to meet."

    return True, "These clubs can potentially meet in UEFA competitions."

can_play, message = can_meet(club1, club2)

st.markdown("### Result")
color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {color}; color: white; text-align: center; font-weight: bold;'>"
    f"{message}</div>", unsafe_allow_html=True
)
