import streamlit as st
from random import shuffle, choice
import time
import pandas as pd

# --- Setup Streamlit Page ---
st.set_page_config(layout="wide", page_title="Skyjo")
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    .css-1v0mbdj.e115fcil1, .css-1dp5vir.e1f1d6gn3 {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .css-1v0mbdj .st-bw, .css-1dp5vir .st-bw {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Card Setup ---
CARD_VALUES = [-2]*5 + [-1]*10 + [0]*15 + [1]*10 + [2]*10 + [3]*10 + [4]*10 + [5]*10 + [6]*10 + [7]*10 + [8]*10 + [9]*10 + [10]*5

# --- Helper Functions ---
def get_card_color(value):
    if value in [-2, -1]: return "#8B5CF6"
    elif value == 0: return "#60A5FA"
    elif value == 1: return "#A7F3D0"
    elif 2 <= value <= 4: return "#4ADE80"
    elif 5 <= value <= 8: return "#FACC15"
    else: return "#F87171"

def init_grid(deck):
    return [[>
    if st.session_state.user_turn:
    turn_text = f"🟢 {st.session_state.player_name}'s Turn"
else:
    turn_text = "🤖 Computer Turn"
st.markdown(f"<h4 style='text-align:center;'>{turn_text}</h4>", unsafe_allow_html=True)

# Display Score
st.info(f"Total Scores → {st.session_state.player_name}: {st.session_state.user_total} | Computer: {st.session_state.comp_total}")

# Draw and Discard
st.subheader("Draw & Discard")
draw_col, discard_col = st.columns(2)

if st.session_state.user_turn and st.session_state.selected_card is None:
    with draw_col:
        if st.button("🃏 Draw from Pile"):
            if st.session_state.draw_pile:
                st.session_state.selected_card = st.session_state.draw_pile.pop()
    with discard_col:
        st.write(f"Top Discard: {st.session_state.discard_pile[-1]}")
        if st.button("📥 Take Discard"):
            st.session_state.selected_card = st.session_state.discard_pile.pop()

if st.session_state.selected_card is not None:
    color = get_card_color(st.session_state.selected_card)
    st.markdown(f"<div style='background-color:{color}; padding:12px; text-align:center; border-radius:10px; font-size:20px;'>Selected: {st.session_state.selected_card}</div>", unsafe_allow_html=True)
    if st.button("🗑 Discard Selected Card"):
        st.session_state.discard_pile.append(st.session_state.selected_card)
        st.session_state.selected_card = None
        reveal_random_card(st.session_state.user_grid)
        st.session_state.user_turn = False
        st.experimental_rerun()

# Display User and Computer Grids
left, right = st.columns(2)

def render_grid(grid, name, editable=False):
    st.markdown(f"#### {name}'s Grid")
    for r in range(3):
        cols = st.columns(len(grid))
        for c in range(len(grid)):
            card = grid[c][r]
            key = f"{name}_{r}_{c}"
            if card['revealed']:
                cols[c].markdown(f"<div style='background-color:{get_card_color(card['value'])}; padding:10px; text-align:center; border-radius:10px;'>
                <strong>{card['value']}</strong></div>", unsafe_allow_html=True)
            elif editable and st.session_state.selected_card is None:
                if cols[c].button("❓", key=key):
                    card['revealed'] = True
                    st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid, show_feedback=True)
                    st.session_state.user_turn = False
                    st.experimental_rerun()
            elif editable and st.session_state.selected_card is not None:
                if cols[c].button("Swap", key=key):
                    st.session_state.discard_pile.append(card['value'])
                    card['value'] = st.session_state.selected_card
                    card['revealed'] = True
                    st.session_state.selected_card = None
                    st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid, show_feedback=True)
                    st.session_state.user_turn = False
                    st.experimental_rerun()
            else:
                cols[c].markdown("❓")

with left:
    render_grid(st.session_state.user_grid, st.session_state.player_name, editable=True)

with right:
    render_grid(st.session_state.comp_grid, "Computer", editable=False)

# Computer Turn (Simplified)
if not st.session_state.user_turn and not st.session_state.game_over:
    if st.button("▶️ Let Computer Play"):
        move = choice(['flip', 'draw'])
        if move == 'flip':
            reveal_random_card(st.session_state.comp_grid)
            st.session_state.comp_grid = remove_matching_columns(st.session_state.comp_grid)
        st.session_state.user_turn = True
        st.experimental_rerun()


