import streamlit as st
import json

@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()
sorted_clubs = sorted(clubs_data, key=lambda x: x["club"])
club_names = [club["club"] for club in sorted_clubs]

def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = get_club_info(selected_club_1)

    if club1 and club1.get("crest_url"):
        st.image(club1["crest_url"], width=100)

    if club1:
        st.markdown(f"**Country:** {club1['country']}")
        st.markdown(f"**Competition:** {club1['competition']}")
        st.markdown(f"**Entry Stage:** {club1.get('entry_stage', 'N/A')}")
        if club1.get("path"):
            st.markdown(f"**Path:** {club1['path']}")

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")
    club2 = get_club_info(selected_club_2)

    if club2 and club2.get("crest_url"):
        st.image(club2["crest_url"], width=100)

    if club2:
        st.markdown(f"**Country:** {club2['country']}")
        st.markdown(f"**Competition:** {club2['competition']}")
        st.markdown(f"**Entry Stage:** {club2.get('entry_stage', 'N/A')}")
        if club2.get("path"):
            st.markdown(f"**Path:** {club2['path']}")

# Helper to identify if a club can drop from one competition to another based on stage
def drops_to_competition(club):
    # Simplified mapping for this example; extend as needed
    comp = club["competition"]
    stage = club.get("entry_stage", "").lower()
    
    if comp == "UCL":
        # UCL losers drop to UEL depending on stage
        if stage.startswith("q1"):
            return ("UEL", "Q2")
        elif stage.startswith("q2"):
            return ("UEL", "Q3")
        elif stage.startswith("q3") or stage.startswith("playoff"):
            return ("UEL", "Group Stage")
        else:
            return None
    elif comp == "UEL":
        # UEL losers drop to UECL depending on stage
        if stage.startswith("q1"):
            return ("UECL", "Q2")
        elif stage.startswith("q2"):
            return ("UECL", "Q3")
        elif stage.startswith("q3") or stage.startswith("playoff"):
            return ("UECL", "Group Stage")
        else:
            return None
    else:
        return None

def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Same country and same competition restriction in group stage
    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, ("These clubs are from the same country and in the same competition. "
                      "Due to UEFA rules, they can only meet **after** the Group Stage.")

    # Russian clubs currently suspended example
    if "Russia" in [club1["country"], club2["country"]]:
        return False, "Russian clubs are suspended from UEFA competitions."

    # Political restrictions example
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan"),
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"Clubs from {c1} and {c2} are not allowed to face each other in UEFA competitions."

    # Check if clubs are in the same competition
    if club1["competition"] == club2["competition"]:
        return True, f"Both clubs compete in the {club1['competition']} and can potentially meet depending on the tournament draw and stages."

    # Check if one can drop from one competition to another where the other club is present
    club1_drops = drops_to_competition(club1)
    club2_drops = drops_to_competition(club2)

    # club1 drops into club2's competition
    if club1_drops and club1_drops[0] == club2["competition"]:
        return True, (f"{club1['club']} starts in {club1['competition']} {club1['entry_stage']} and if they lose, "
                      f"they drop to {club2['competition']} {club1_drops[1]}, where they might meet {club2['club']}.")

    # club2 drops into club1's competition
    if club2_drops and club2_drops[0] == club1["competition"]:
        return True, (f"{club2['club']} starts in {club2['competition']} {club2['entry_stage']} and if they lose, "
                      f"they drop to {club1['competition']} {club2_drops[1]}, where they might meet {club1['club']}.")

    # Otherwise, different competitions and no known drop path
    return False, (f"{club1['club']} competes in {club1['competition']} and {club2['club']} in {club2['competition']}. "
                   "They are unlikely to meet this season unless competition rules change.")

can_play, message = can_meet(club1, club2)

st.markdown("### Result")
color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {color}; color: white; text-align: center; font-size: 1.2em;'>"
    f"{message}"
    "</div>",
    unsafe_allow_html=True,
)
