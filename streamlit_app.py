import streamlit as st
import json

# Map short stages to full plain English
stage_names = {
    "q1": "First Qualifying Round",
    "q2": "Second Qualifying Round",
    "q3": "Third Qualifying Round",
    "playoff": "Playoff Round",
    "group stage": "Group Stage",
    "r32": "Round of 32",
    "r16": "Round of 16",
    "quarterfinal": "Quarterfinals",
    "semifinal": "Semifinals",
    "final": "Final",
}

def pretty_stage(stage_raw: str) -> str:
    if not stage_raw:
        return "N/A"
    stage_lower = stage_raw.lower()
    for key in stage_names:
        if key in stage_lower:
            rest = stage_raw[len(key):].strip()
            return stage_names[key] + (" " + rest if rest else "")
    return stage_raw

# Load clubs data from JSON
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Sort clubs alphabetically by club name
sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

# UI: Club selection dropdowns
col1, col2 = st.columns(2)
with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")

# Helper: get club info by name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

# Display club crests above dropdowns (optional, if you have URLs)
with col1:
    if club1 and club1.get("crest_url"):
        st.image(club1["crest_url"], width=100)
with col2:
    if club2 and club2.get("crest_url"):
        st.image(club2["crest_url"], width=100)

# Display club info below dropdowns, without repeating name
with col1:
    if club1:
        st.markdown(f"**Country:** {club1['country']}")
        st.markdown(f"**Competition:** {club1['competition']}")
        st.markdown(f"**Entry Stage:** {pretty_stage(club1.get('entry_stage', 'N/A'))}")
        if club1.get("path"):
            st.markdown(f"**Path:** {club1['path']}")
with col2:
    if club2:
        st.markdown(f"**Country:** {club2['country']}")
        st.markdown(f"**Competition:** {club2['competition']}")
        st.markdown(f"**Entry Stage:** {pretty_stage(club2.get('entry_stage', 'N/A'))}")
        if club2.get("path"):
            st.markdown(f"**Path:** {club2['path']}")

# Logic to determine if clubs can meet (more strict, simplified example)
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Same country restriction applies only in Group Stage of same competition
    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, "These clubs can meet only after the Group Stage due to same-country restriction."

    # Suspended countries example (customize as needed)
    suspended_countries = ["Russia"]
    if club1["country"] in suspended_countries or club2["country"] in suspended_countries:
        return False, "One or both clubs are from suspended countries and cannot meet."

    # Political restrictions (simplified)
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan"),
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"Clubs from {c1} and {c2} are not allowed to meet."

    # More refined logic based on competition and entry stage
    # Example: If UCL club lost in Q2, goes to UEL, might meet certain clubs there, etc.
    # This would require more detailed competition progression logic, here simplified:

    # If competitions are different, allow meeting only if path of relegation possible
    comp_pairs_allowed = {
        ("UCL", "UEL"),
        ("UEL", "UECL"),
        ("UEL", "UCL"),
        ("UECL", "UEL"),
    }
    if (club1["competition"], club2["competition"]) not in comp_pairs_allowed and club1["competition"] != club2["competition"]:
        return False, "Clubs in these different competitions typically do not meet."

    # You can add custom logic based on entry_stage to refine probabilities or restrictions here

    return True, f"These clubs can potentially meet in {club1['competition']} or {club2['competition']} depending on results."

can_play, message = can_meet(club1, club2)

# Display result with color feedback
st.markdown("### Result")
result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.2em;'>"
    f"{message}"
    "</div>",
    unsafe_allow_html=True,
)
