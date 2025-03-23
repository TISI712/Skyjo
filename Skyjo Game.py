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
    return [[{'value': deck.pop(), 'revealed': False} for _ in range(3)] for _ in range(4)]

def all_revealed(grid):
    return all(card['revealed'] for col in grid for card in col)

def calculate_score(grid):
    return sum(card['value'] for col in grid for card in col if card['revealed'])

def remove_matching_columns(grid, show_feedback=False):
    new_grid = []
    for col in grid:
        if all(card['revealed'] for card in col):
            values = [card['value'] for card in col]
            if all(v == values[0] for v in values):
                if show_feedback:
                    st.info(f"Removed column with three {values[0]}s!")
                continue
        new_grid.append(col)
    return new_grid

def reveal_random_card(grid):
    hidden = [(c, r) for c in range(len(grid)) for r in range(3) if not grid[c][r]['revealed']]
    if hidden:
        col, row = choice(hidden)
        grid[col][row]['revealed'] = True
        return col, row
    return None, None

def setup_new_round():
    shuffle(CARD_VALUES)
    st.session_state.draw_pile = CARD_VALUES[:-1]
    st.session_state.discard_pile = [CARD_VALUES[-1]]
    st.session_state.user_grid = init_grid(st.session_state.draw_pile)
    st.session_state.comp_grid = init_grid(st.session_state.draw_pile)
    st.session_state.selected_card = None
    st.session_state.game_over = False
    st.session_state.message_log.append("--- New Round ---")

    for _ in range(2):
        reveal_random_card(st.session_state.user_grid)
        reveal_random_card(st.session_state.comp_grid)

    user_sum = calculate_score(st.session_state.user_grid)
    comp_sum = calculate_score(st.session_state.comp_grid)
    if user_sum > comp_sum:
        st.session_state.user_turn = True
        st.session_state.round_starter = "user"
        st.session_state.message_log.append(f"{st.session_state.player_name} starts the round.")
    else:
        st.session_state.user_turn = False
        st.session_state.round_starter = "comp"
        st.session_state.message_log.append("Computer starts the round.")

# --- Initial Setup Page ---
if 'setup_complete' not in st.session_state:
    st.title("🎮 Welcome to Skyjo Tournament Mode")
    st.subheader("Player Setup")
    name = st.text_input("Enter your name:", value="Player")
    target = st.number_input("Game ends when someone reaches this score:", min_value=50, max_value=200, value=100)

    start_game = st.button("Start Game")

    if start_game and name.strip():
        st.session_state.player_name = name
        st.session_state.target_score = target
        st.session_state.user_total = 0
        st.session_state.comp_total = 0
        st.session_state.round_starter = None
        st.session_state.message_log = []
        st.session_state.history = []
        st.session_state.setup_complete = True
        setup_new_round()
        st.experimental_rerun()
    else:
        st.stop()

# If setup is complete, continue with game logic
st.write("✅ Setup complete. Game will continue...")
# --- Gameplay Logic ---

# Display Turn Indicator
if not st.session_state.game_over:
    turn_text = f"🟢 {st.session_state.player_name}'s Turn" if st.session_state.user_turn else "🤖 Computer Turn"
turn_text = f"🟢 {st.session_state.player_name}'s Turn" if st.session_state.user_turn else "🤖 Computer Turn"
st.markdown(f"<h4 style='text-align:center;'>{turn_text}</h4>", unsafe_allow_html=True)>
    {'🟢 ' + st.session_state.player_name + "'s Turn" if st.session_state.user_turn else '🤖 Computer Turn'}</h4>", unsafe_allow_html=True)

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
