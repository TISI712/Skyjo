import streamlit as st
from random import shuffle, choice
import time

# --- Card Setup ---
CARD_VALUES = [-2]*5 + [-1]*10 + [0]*15 + [1]*10 + [2]*10 + [3]*10 + [4]*10 + [5]*10 + [6]*10 + [7]*10 + [8]*10 + [9]*10 + [10]*5
shuffle(CARD_VALUES)

# --- Helper Functions ---
def get_card_color(value):
    if value in [-2, -1]:
        return "#8B5CF6"  # purple
    elif value == 0:
        return "#60A5FA"  # blue
    elif value == 1:
        return "#A7F3D0"  # light green
    elif 2 <= value <= 4:
        return "#4ADE80"  # green
    elif 5 <= value <= 8:
        return "#FACC15"  # yellow
    else:
        return "#F87171"  # red

def init_grid(deck):
    return [[{'value': deck.pop(), 'revealed': False} for _ in range(3)] for _ in range(4)]  # 4 columns x 3 rows

def all_revealed(grid):
    return all(card['revealed'] for col in grid for card in col)

def calculate_score(grid):
    return sum(card['value'] for col in grid for card in col if card['revealed'])

def remove_matching_columns(grid):
    new_grid = []
    for col in grid:
        if all(card['revealed'] for card in col):
            values = [card['value'] for card in col]
            if all(v == values[0] for v in values):
                continue  # skip column (remove it)
        new_grid.append(col)
    return new_grid

# --- Session State Init ---
if 'draw_pile' not in st.session_state:
    st.session_state.draw_pile = CARD_VALUES[:-1]
    st.session_state.discard_pile = [CARD_VALUES[-1]]
    st.session_state.user_grid = init_grid(st.session_state.draw_pile)
    st.session_state.comp_grid = init_grid(st.session_state.draw_pile)
    st.session_state.user_turn = True
    st.session_state.selected_card = None
    st.session_state.game_over = False
    st.session_state.show_tutorial = True
    st.session_state.user_score = 0
    st.session_state.comp_score = 0

# --- Title ---
st.title("🎯 Skyjo - Two Player Game")

# --- Turn Indicator ---
if not st.session_state.game_over:
    turn_text = "🟢 Your Turn" if st.session_state.user_turn else "🤖 Computer's Turn"
    st.markdown(f"<h4 style='text-align:center; color:#333;'>{turn_text}</h4>", unsafe_allow_html=True)

# --- Tutorial ---
if st.session_state.show_tutorial:
    with st.expander("📘 How to Play (click to expand)"):
        st.markdown("""
        - You and the computer each have 12 cards, arranged in a 4x3 grid.
        - Click a ❓ to reveal a card, or draw a card and swap with one in your grid.
        - The replaced card goes to the discard pile.
        - If all cards in a column are revealed and equal, the column is removed.
        - Turns alternate between you and the computer.
        - Game ends when all cards in your grid are revealed.
        """)

# --- Game End Check ---
if all_revealed(st.session_state.user_grid):
    st.session_state.game_over = True
    st.session_state.user_score = calculate_score(st.session_state.user_grid)
    st.session_state.comp_score = calculate_score(st.session_state.comp_grid)
    st.success("🎉 Game Over! You've revealed all your cards!")
    time.sleep(0.5)
    st.balloons()
    with st.expander("📊 Final Scores"):
        st.markdown(f"**Your Score:** {st.session_state.user_score}")
        st.markdown(f"**Computer Score:** {st.session_state.comp_score}")
        if st.session_state.user_score < st.session_state.comp_score:
            st.success("You win! 🎉")
        elif st.session_state.user_score > st.session_state.comp_score:
            st.warning("Computer wins! 🤖")
        else:
            st.info("It's a tie! 🟰")

# --- Draw / Discard ---
if not st.session_state.game_over:
    st.subheader("Draw and Discard Piles")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.user_turn and st.session_state.selected_card is None:
            if st.button("Draw Card", help="Draw a new card from the pile"):
                if st.session_state.draw_pile:
                    st.session_state.selected_card = st.session_state.draw_pile.pop()
    with col2:
        st.write(f"Top Discard: {st.session_state.discard_pile[-1]}")
        if st.session_state.user_turn and st.session_state.selected_card is None:
            if st.button("Take Discard", help="Take the top card from discard pile"):
                st.session_state.selected_card = st.session_state.discard_pile.pop()

    if st.session_state.selected_card is not None:
        color = get_card_color(st.session_state.selected_card)
        st.markdown(f"<div style='background-color:{color}; padding:16px; margin-top:10px; text-align:center; border-radius:12px; font-size:24px; font-weight:bold;'>Drawn Card: {st.session_state.selected_card}</div>", unsafe_allow_html=True)

# --- User Grid (4 Columns x 3 Rows) ---
st.subheader("Your Grid")
rows = 3
cols = len(st.session_state.user_grid)
for r in range(rows):
    grid_row = st.columns(cols)
    for c in range(cols):
        card = st.session_state.user_grid[c][r]
        key = f"user_{r}_{c}"
        if card['revealed']:
            color = get_card_color(card['value'])
            grid_row[c].markdown(f"<div style='background-color:{color}; padding:12px; text-align:center; border-radius:10px;'><strong>{card['value']}</strong></div>", unsafe_allow_html=True)
        else:
            if st.session_state.user_turn:
                if st.session_state.selected_card is None:
                    if grid_row[c].button("❓", key=key, help="Click to reveal this card"):
                        card['revealed'] = True
                        st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid)
                        st.session_state.user_turn = False
                else:
                    if grid_row[c].button("Swap", key=key, help="Swap with drawn card"):
                        st.session_state.discard_pile.append(card['value'])
                        card['value'] = st.session_state.selected_card
                        card['revealed'] = True
                        st.session_state.selected_card = None
                        st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid)
                        st.session_state.user_turn = False
                        st.rerun()

# --- Computer Turn ---
if not st.session_state.user_turn and not st.session_state.game_over and st.session_state.selected_card is None:
    time.sleep(0.5)
    action = choice(['draw', 'discard', 'flip'])
    if action == 'flip':
        hidden = [(c, r) for c in range(len(st.session_state.comp_grid)) for r in range(3) if not st.session_state.comp_grid[c][r]['revealed']]
        if hidden:
            col, row = choice(hidden)
            st.session_state.comp_grid[col][row]['revealed'] = True
            st.session_state.comp_grid = remove_matching_columns(st.session_state.comp_grid)
    st.session_state.user_turn = True

# --- Restart ---
if st.button("🔁 Restart Game"):
    shuffle(CARD_VALUES)
    st.session_state.draw_pile = CARD_VALUES[:-1]
    st.session_state.discard_pile = [CARD_VALUES[-1]]
    st.session_state.user_grid = init_grid(st.session_state.draw_pile)
    st.session_state.comp_grid = init_grid(st.session_state.draw_pile)
    st.session_state.user_turn = True
    st.session_state.selected_card = None
    st.session_state.game_over = False
    st.session_state.user_score = 0
    st.session_state.comp_score = 0
    st.session_state.show_tutorial = False
    st.rerun()
