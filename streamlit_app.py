import streamlit as st
import json

# Load club data
@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs_data = load_clubs()

# Create a dictionary for quick access
club_dict = {club['name']: club for club in clubs_data}
club_names = list(club_dict.keys())

# Function to simulate competition path logic
def can_meet(club1, club2):
    if club1['country'] == club2['country']:
        if club1['competition'] == club2['competition'] and club1['entry_stage'] == "Group Stage":
            return False, "Clubs from the same country cannot meet in the group stage."

    # Exclusion rules
    exclusions = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan"),
        ("Russia", None)
    ]

    for c1, c2 in exclusions:
        if (club1['country'] == c1 and club2['country'] == c2) or (club1['country'] == c2 and club2['country'] == c1):
            return False, f"Due to geopolitical rules, clubs from {c1} and {c2} cannot meet."
        if club1['country'] == c1 or club2['country'] == c1:
            if c2 is None:
                return False, f"Clubs from {c1} are currently excluded from UEFA competitions."

    # Determine possible competitions via path rules
    def get_possible_comps(club):
        comp = club['competition']
        stage = club['entry_stage']
        if comp == 'UCL':
            if stage in ['Q1', 'Q2', 'Q3', 'PO']:
                return ['UCL', 'UEL', 'UECL']
            else:
                return ['UCL']
        elif comp == 'UEL':
            if stage in ['Q2', 'Q3', 'PO']:
                return ['UEL', 'UECL']
            else:
                return ['UEL']
        elif comp == 'UECL':
            return ['UECL']
        return [comp]

    comps1 = set(get_possible_comps(club1))
    comps2 = set(get_possible_comps(club2))

    shared = comps1 & comps2
    if shared:
        shared_str = ', '.join(shared)
        return True, f"Yes, the clubs can meet in: {shared_str}."
    else:
        return False, "They play in separate competitions with no overlapping stages."

# Streamlit UI
st.set_page_config(page_title="UEFA Club Meeting Checker", layout="wide")
st.title("UEFA 2025–26 Club Meeting Possibility")

col1, col2 = st.columns([1, 1])

with col1:
    club1_name = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = club_dict[club1_name]
    st.image(club1.get("crest", ""), width=64)

with col2:
    club2_name = st.selectbox("Select Club 2", club_names, key="club2")
    club2 = club_dict[club2_name]
    st.image(club2.get("crest", ""), width=64)

can_play, reason = can_meet(club1, club2)

color = "#d4edda" if can_play else "#f8d7da"
st.markdown(f"""
<div style='margin-top: 20px; padding: 20px; background-color: {color}; border-radius: 8px; border: 1px solid #ccc;'>
  <strong>Can they meet?</strong><br>
  {reason}
</div>
""", unsafe_allow_html=True)
