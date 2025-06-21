import streamlit as st
import json

@st.cache_data
def load_clubs():
    with open("clubs.json", "r", encoding="utf-8") as f:
        return json.load(f)

clubs = load_clubs()

st.title("UEFA Clubs Meeting Predictor")

club_names = [club["name"] for club in clubs]

col1, col2 = st.columns(2)
with col1:
    club1 = st.selectbox("Select first club", club_names)
with col2:
    club2 = st.selectbox("Select second club", club_names)

def can_meet(club1_name, club2_name):
    # Simplified logic example:
    if club1_name == club2_name:
        return False, "Same club chosen."
    # Add your full UEFA rules logic here
    return True, f"{club1_name} and {club2_name} can meet."

if club1 and club2:
    meet, message = can_meet(club1, club2)
    color = "green" if meet else "red"
    st.markdown(f"<div style='color: {color}; font-weight: bold;'>{message}</div>", unsafe_allow_html=True)
