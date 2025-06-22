import streamlit as st
import json

# Load clubs data from JSON
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Helper to get club info by name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

# Sort clubs alphabetically
sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Club 1 Crest")
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = get_club_info(selected_club_1)
    if club1 and club1.get("crest_url"):
        st.image(club1["crest_url"], width=100)
    st.markdown(f"Country: {club1['country']}")

with col2:
    st.markdown("### Club 2 Crest")
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")
    club2 = get_club_info(selected_club_2)
    if club2 and club2.get("crest_url"):
        st.image(club2["crest_url"], width=100)
    st.markdown(f"Country: {club2['country']}")

st.markdown("### Club Info")

info_col1, info_col2 = st.columns(2)
with info_col1:
    if club1:
        st.markdown(f"**Competition:** {club1['competition']}")
        st.markdown(f"**Entry Stage:** {club1['entry_stage']}")
        if club1.get("path"):
            st.markdown(f"**Path:** {club1['path']}")

with info_col2:
    if club2:
        st.markdown(f"**Competition:** {club2['competition']}")
        st.markdown(f"**Entry Stage:** {club2['entry_stage']}")
        if club2.get("path"):
            st.markdown(f"**Path:** {club2['path']}")

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

st.markdown("### Result")
result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; text-align: center; font-size: 1.2em;'>"
    f"{message}"
    f"</div>",
    unsafe_allow_html=True
)
