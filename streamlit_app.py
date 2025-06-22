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

# Entry stage code to full name
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

# Select clubs UI
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

# Helper: define stage order for comparison
stages_order = ["Q1", "Q2", "Q3", "PO", "GS", "R16", "QF", "SF", "F"]

# Define competition flow (who can drop where)
# For example, UCL Q2 losers enter UEL Q3, etc.
competition_flow = {
    "UCL": {
        "Q1": ("UCL", "Q2"),  # winners go up in UCL qualifiers
        "Q2": ("UEL", "Q3"),  # losers drop to UEL Q3
        "Q3": ("UEL", "PO"),  # losers drop to UEL PO
        "PO": ("UEL", "GS"),  # losers drop to UEL GS
        "GS": ("UCL", None),  # group stage
        # knockout stages stay in UCL
    },
    "UEL": {
        "Q1": ("UEL", "Q2"),
        "Q2": ("UEL", "Q3"),
        "Q3": ("UECL", "PO"),
        "PO": ("UEL", "GS"),
        "GS": ("UEL", None),
    },
    "UECL": {
        "Q1": ("UECL", "Q2"),
        "Q2": ("UECL", "PO"),
        "PO": ("UECL", "GS"),
        "GS": ("UECL", None),
    }
}

def stage_index(stage_code):
    try:
        return stages_order.index(stage_code)
    except ValueError:
        return -1

def can_meet(club1, club2):
    # Basic checks
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    c1_name = club1["club"]
    c2_name = club2["club"]
    comp1, comp2 = club1["competition"], club2["competition"]
    stage1, stage2 = club1.get("entry_stage"), club2.get("entry_stage")
    country1, country2 = club1["country"], club2["country"]

    # Check geopolitical exclusions
    blocked_pairs = [
        {"Serbia", "Kosovo"},
        {"Armenia", "Azerbaijan"},
    ]
    for pair in blocked_pairs:
        if {country1, country2} == pair:
            return False, f"Clubs from {country1} and {country2} cannot meet due to geopolitical restrictions."

    # Same country restriction in group stage and early knockouts
    if country1 == country2 and comp1 == comp2:
        # No same country teams in group stage
        if "GS" in (stage1, stage2):
            return False, f"Same-country clubs cannot meet in the Group Stage of {comp1}."
        # No same country teams in round of 16 of UCL and UEL
        if comp1 in ["UCL", "UEL"]:
            if "R16" in (stage1, stage2):
                return False, f"Same-country clubs cannot meet in the Round of 16 of {comp1}."

    # If clubs in different competitions, check if path exists
    if comp1 != comp2:
        # Check if club1 can drop to comp2 stage or vice versa via competition flow
        def path_exists(from_comp, from_stage, to_comp, to_stage):
            # Recursively check if from_comp/stage can drop to to_comp/to_stage
            current_comp, current_stage = from_comp, from_stage
            for _ in range(5):  # avoid infinite loops, max depth
                if current_comp == to_comp and current_stage == to_stage:
                    return True
                if current_stage not in competition_flow.get(current_comp, {}):
                    break
                next_comp, next_stage = competition_flow[current_comp][current_stage]
                if not next_stage:
                    break
                current_comp, current_stage = next_comp, next_stage
            return False

        if path_exists(comp1, stage1, comp2, stage2):
            return True, f"{c1_name} may face {c2_name} after dropping from {comp1} {stage_full_names.get(stage1, stage1)} to {comp2} {stage_full_names.get(stage2, stage2)}."
        if path_exists(comp2, stage2, comp1, stage1):
            return True, f"{c2_name} may face {c1_name} after dropping from {comp2} {stage_full_names.get(stage2, stage2)} to {comp1} {stage_full_names.get(stage1, stage1)}."
        return False, f"No direct competition path to meet between {c1_name} in {comp1} and {c2_name} in {comp2} at their stages."

    # If same competition, check stage overlap
    idx1 = stage_index(stage1)
    idx2 = stage_index(stage2)

    if idx1 == -1 or idx2 == -1:
        return False, "Unknown stages for one or both clubs."

    # They can meet if stages overlap or one stage immediately precedes another (allowing knockouts etc)
    if abs(idx1 - idx2) > 2:
        return False, f"Clubs are at very different stages ({stage_full_names.get(stage1, stage1)} vs {stage_full_names.get(stage2, stage2)}) and unlikely to meet."

    # Additional checks for knockout stages
    knockout_stages = ["R16", "QF", "SF", "F"]
    if stage1 in knockout_stages and stage2 in knockout_stages:
        # Same knockout round or adjacent rounds can meet (e.g. QF vs SF is unlikely but possible later)
        # Simplify: allow meeting if rounds are same or differ by 1
        if abs(idx1 - idx2) > 1:
            return False, f"Clubs are at knockout stages too far apart ({stage_full_names.get(stage1, stage1)} vs {stage_full_names.get(stage2, stage2)})."

    return True, f"{c1_name} and {c2_name} can potentially meet in {comp1} during or after the {stage_full_names.get(stage1, stage1)}."

can_play, message =
