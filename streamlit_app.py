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

# Competition logos URLs (SVG or PNG links)
competition_logos = {
    "UCL": "https://upload.wikimedia.org/wikipedia/en/3/3a/UEFA_Champions_League_logo_2.svg",
    "UEL": "https://upload.wikimedia.org/wikipedia/en/f/f8/UEFA_Europa_League_logo_2021.svg",
    "UECL": "https://upload.wikimedia.org/wikipedia/en/6/6a/UEFA_Conference_League_logo.svg"
}

# Club selection UI
col1, col2 = st.columns(2)

with col1:
    selected_club_1 = st.selectbox("Select Club 1", club_names, key="club1")

with col2:
    selected_club_2 = st.selectbox("Select Club 2", club_names, key="club2")

# Retrieve full club info by club name
def get_club_info(name):
    return next((club for club in clubs_data if club["club"] == name), None)

club1 = get_club_info(selected_club_1)
club2 = get_club_info(selected_club_2)

# Function to display crest + competition logo side by side
def show_club_and_competition_images(club):
    img_col1, img_col2 = st.columns([1, 0.75])  # competition logo is 75% width of crest approx

    with img_col1:
        if club.get("crest_url"):
            st.image(club["crest_url"], width=120)
        else:
            st.write("No crest available")

    with img_col2:
        comp_logo_url = competition_logos.get(club["competition"])
        if comp_logo_url:
            st.image(comp_logo_url, width=90)  # 75% of 120 is 90
        else:
            st.write("No competition logo available")

# Display club 1 images and entry stage info
with col1:
    show_club_and_competition_images(club1)
    st.markdown(f"**Entry Stage:** {club1.get('entry_stage', 'Unknown')}")

# Display club 2 images and entry stage info
with col2:
    show_club_and_competition_images(club2)
    st.markdown(f"**Entry Stage:** {club2.get('entry_stage', 'Unknown')}")

# Logic to determine if clubs can meet
def can_meet(club1, club2):
    if not club1 or not club2 or club1 == club2:
        return False, "Invalid club selection."

    # Same country clubs can't meet in Group Stage
    if club1["country"] == club2["country"] and club1["competition"] == club2["competition"]:
        return True, "They can only meet after the Group Stage due to same-country restriction."

    # Russian clubs currently suspended (example logic)
    if "Russia" in [club1["country"], club2["country"]]:
        return False, "Russian clubs are suspended from UEFA competitions."

    # Serbia vs Kosovo, Armenia vs Azerbaijan exclusions (simplified)
    blocked_pairs = [
        ("Serbia", "Kosovo"),
        ("Armenia", "Azerbaijan")
    ]
    for c1, c2 in blocked_pairs:
        if {club1["country"], club2["country"]} == {c1, c2}:
            return False, f"{c1} and {c2} clubs are not allowed to meet in UEFA competitions."

    # Add further detailed logic here if needed

    return True, "These clubs can potentially meet in UEFA competitions."

can_play, message = can_meet(club1, club2)

# Display result with color feedback
st.markdown("### Result")
result_color = "green" if can_play else "red"
st.markdown(
    f"<div style='padding: 1em; background-color: {result_color}; color: white; "
    f"text-align: center; font-size: 1.2em;'>{message}</div>",
    unsafe_allow_html=True
)
