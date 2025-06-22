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

# Function to get full club info by name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

# Logic function to check if two clubs can meet
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Same country clubs can't meet in Group Stage of same competition
    if (club1["country"] == club2["country"] and 
        club1["competition"] == club2["competition"] and
        club1.get("entry_stage") == "Group Stage" and
        club2.get("entry_stage") == "Group Stage"):
        return False, "Clubs from the same country cannot meet in the Group Stage."

    # Russian clubs suspended example
    if "Russia" in [club1["country"], club2["country"]]:
        return False, "Russian clubs are suspended from UEFA competitions."

    # Specific country conflicts
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan")
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"{c1} and {c2} clubs cannot meet in UEFA competitions."

    # Clubs in different competitions can't meet (unless later stage, ignored here for simplicity)
    if club1["competition"] != club2["competition"]:
        return False, "Clubs in different competitions cannot meet at this stage."

    # Example: clubs in early qualifying rounds can't meet group stage clubs
    early_stages = ["Q1", "Q2", "Q3", "Play-offs"]
    if (club1.get("entry_stage") in early_stages and club2.get("entry_stage") == "Group Stage") or \
       (club2.get("entry_stage") in early_stages and club1.get("entry_stage") == "Group Stage"):
        return False, "Clubs in early qualifying rounds do not meet group stage clubs yet."

    # You can add more rules here as needed

    return True, "These clubs can potentially meet in UEFA competitions."

# UI

st.title("UEFA Clubs Meeting Eligibility Checker")

col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")
    club1 = get_club_info(selected_club_1)
    if club1 and club1.get("crest_url"):
        st.image(club1["crest_url"], width=100)

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")
    club2 = get_club_info(selected_club_2)
    if club2 and club2.get("crest_url"):
        st.image(club2["crest_url"], width=100)

# Run logic
can_play, message = can_meet(club1, club2)

# Result display
result_color = "green" if can_play else "red"
st.markdown(
    f"""
    <div style='padding: 1em; background-color: {result_color}; color: white; 
                text-align: center; font-size: 1.2em; margin-top: 20px;'>
        {message}
    </div>
    """,
    unsafe_allow_html=True,
)
