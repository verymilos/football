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

# Competition logos URLs (static, from Wikipedia)
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/f/f5/UEFA_Champions_League.svg",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/7/73/UEFA_Europa_League_2024.png",
    "UECL": "https://upload.wikimedia.org/wikipedia/commons/4/4b/UEFA_Conference_League_full_logo_%282024_version%29.svg",
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

def image_html(url, height=100):
    return f"<img src='{url}' height='{height}' style='vertical-align: middle; object-fit: contain;'/>"

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
            st.markdown(image_html(crest_url, 120), unsafe_allow_html=True)
        else:
            st.write("No crest available")
    with c2:
        if comp in competition_logos:
            st.markdown(image_html(competition_logos[comp]), unsafe_allow_html=True)
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
competition_flow = {
    "UCL": {
        "Q1": ("UCL", "Q2"),
        "Q2": ("UEL", "Q3"),
        "Q3": ("UEL", "PO"),
        "PO": ("UEL", "GS"),
        "GS": ("UCL", None),
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
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    c1_name = club1["club"]
    c2_name = club2["club"]
    comp1, comp2 = club1["competition"], club2["competition"]
    stage1, stage2 = club1.get("entry_stage"), club2.get("entry_stage")
    country1, country2 = club1["country"], club2["country"]

    # Geopolitical restrictions
    blocked_pairs = [
        {"Serbia", "Kosovo"},
        {"Armenia", "Azerbaijan"},
    ]
    for pair in blocked_pairs:
        if {country1, country2} == pair:
            return False, f"Clubs from {country1} and {country2} cannot meet due to geopolitical restrictions."

    # Same country restrictions for group stage and R16 in UCL and UEL
    if country1 == country2 and comp1 == comp2:
        if "GS" in (stage1, stage2):
            return False, f"Same-country clubs cannot meet in the Group Stage of {comp1}."
        if comp1 in ["UCL", "UEL"]:
            if "R16" in (stage1, stage2):
                return False, f"Same-country clubs cannot meet in the Round of 16 of {comp1}."

    # Different competitions: check if one drops into the other's comp/stage
    if comp1 != comp2:
        def path_exists(from_comp, from_stage, to_comp, to_stage):
            current_comp, current_stage = from_comp, from_stage
            for _ in range(5):
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
        return False, f"No direct competition path for {c1_name} in {comp1} and {c2_name} in {comp2} to meet at these stages."

    # Same competition: compare stages
    idx1 = stage_index(stage1)
    idx2 = stage_index(stage2)
    if idx1 == -1 or idx2 == -1:
        return False, "Unknown stages for one or both clubs."

    # Clubs at very different stages can't meet realistically
    if abs(idx1 - idx2) > 2:
        return False, f"Clubs are at very different stages ({stage_full_names.get(stage1, stage1)} vs {stage_full_names.get(stage2, stage2)}) and unlikely to meet."

    # Knockout stage proximity check
    knockout_stages = ["R16", "QF", "SF", "F"]
    if stage1 in knockout_stages and stage2 in knockout_stages:
        if abs(idx1 - idx2) > 1:
            return False, f"Clubs are at knockout stages too far apart ({stage_full_names.get(stage1, stage1)} vs {stage_full_names.get(stage2, stage2)})."

    return True, f"{c1_name} and {c2_name} can potentially meet in {comp1} during or after the {stage_full_names.get(stage1, stage1)}."

can_play, message = can_meet(club1, club2)

st.markdown("---")
st.markdown(f"### Meeting possibility:")
if can_play:
    st.success(message)
else:
    st.error(message)
