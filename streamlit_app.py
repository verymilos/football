import streamlit as st
import json

@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

stage_full_names = {
    "Q1": "First Qualifying Round",
    "Q2": "Second Qualifying Round",
    "Q3": "Third Qualifying Round",
    "PO": "Playoff Round",
    "GS": "Group Stage",
    "R32": "Round of 32",
    "R16": "Round of 16",
    "QF": "Quarterfinals",
    "SF": "Semifinals",
    "F": "Final"
}

# Use PNG logos for Streamlit compatibility
competition_logos = {
    "UCL": "https://www.citypng.com/photo/2a898f22/uefa-champions-league-official-logo",
    "UEL": "https://www.citypng.com/photo/b3ef997b/uefa-europa-league-logo",
    "UECL": "https://www.fifplay.com/uel-logo/"
}

sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

col1, col2 = st.columns(2)

with col1:
    st.write("### Club 1")
    selected_club_1 = st.selectbox("", club_names, key="club1")

with col2:
    st.write("### Club 2")
    selected_club_2 = st.selectbox("", club_names, key="club2")

def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

def show_club_info(club):
    if not club:
        st.write("Club info missing.")
        return
    c1, c2, c3 = st.columns([1, 0.75, 2])

    with c1:
        crest_url = club.get("crest_url")
        if crest_url:
            st.image(crest_url, width=120)
        else:
            st.write("No crest available")

    with c2:
        comp_logo_url = competition_logos.get(club["competition"])
        if comp_logo_url:
            st.image(comp_logo_url, width=90)  # 75% size of crest
        else:
            st.write("No competition logo")

    with c3:
        entry_stage_name = stage_full_names.get(club["entry_stage"], club["entry_stage"])
        st.markdown(f"**{entry_stage_name}**")

# Place club infos side by side:
info_col1, info_col2 = st.columns(2)

with info_col1:
    show_club_info(club1)

with info_col2:
    show_club_info(club2)

def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Please select two different clubs."

    if club1["competition"] != club2["competition"]:
        if club1["competition"] == "UCL" and club2["competition"] in ("UEL", "UECL"):
            if club1["entry_stage"] in ("Q2", "Q3", "PO") and club2["entry_stage"] in ("Q3", "PO", "GS"):
                return True, f"{club1['club']} could meet {club2['club']} because UCL teams dropping down join later rounds of {club2['competition']}."
        if club2["competition"] == "UCL" and club1["competition"] in ("UEL", "UECL"):
            if club2["entry_stage"] in ("Q2", "Q3", "PO") and club1["entry_stage"] in ("Q3", "PO", "GS"):
                return True, f"{club2['club']} could meet {club1['club']} because UCL teams dropping down join later rounds of {club1['competition']}."
        return False, f"{club1['club']} and {club2['club']} are in different competitions and typically cannot meet."

    if club1["country"] == club2["country"]:
        if club1["entry_stage"] == "GS" and club2["entry_stage"] == "GS":
            return False, "Same country clubs cannot meet in the Group Stage."

    blocked_pairs = [("Serbia", "Kosovo"), ("Armenia", "Azerbaijan")]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"Clubs from {c1} and {c2} cannot meet due to political restrictions."

    stages_order = ["Q1", "Q2", "Q3", "PO", "GS", "R32", "R16", "QF", "SF", "F"]
    stage1_idx = stages_order.index(club1["entry_stage"]) if club1["entry_stage"] in stages_order else -1
    stage2_idx = stages_order.index(club2["entry_stage"]) if club2["entry_stage"] in stages_order else -1

    diff = abs(stage1_idx - stage2_idx)
    if diff > 3:
        return False, "Very unlikely to meet due to large stage difference."

    return True, "These clubs can potentially meet depending on competition progress and draws."

can_play, message = can_meet(club1, club2)

result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.2em;'>"
    f"{message}</div>",
    unsafe_allow_html=True
)
