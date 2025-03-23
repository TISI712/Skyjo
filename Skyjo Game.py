
import streamlit as st
from random import shuffle, choice
import pandas as pd
import time

# --- Page Config and Custom Style ---
st.set_page_config(layout="wide", page_title="Skyjo")
st.markdown("""
<style>
    .block-container {padding-top: 1rem;}
    .stButton>button {
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton>button:hover {background-color: #45a049;}
    .card-style {
        padding: 12px;
        margin: 4px auto;
        border-radius: 12px;
        width: 60px;
        height: 50px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .instructions {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ccc;
        font-size: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class='title'>🃏 Skyjo Tournament Mode</div>""", unsafe_allow_html=True)
st.markdown("""
<div class='instructions'>
<b>How to Play:</b><br>
- On your turn, draw a card or take the top discard.<br>
- You may replace any card (even hidden) with your drawn card, or discard it and flip one hidden card.<br>
- When all your cards are face up, the round ends after the opponent gets one last turn.<br>
- Try to get the lowest score possible! 🎯
</div>
""", unsafe_allow_html=True)

# --- Card Setup ---
def get_card_deck():
    return [-2]*5 + [-1]*10 + [0]*15 + [1]*10 + [2]*10 + [3]*10 + [4]*10 + [5]*10 + [6]*10 + [7]*10 + [8]*10 + [9]*10 + [10]*5

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

def count_revealed(grid):
    return sum(1 for col in grid for card in col if card['revealed'])

def remove_matching_columns(grid):
    new_grid = []
    for col in grid:
        if all(card['revealed'] for card in col):
            values = [card['value'] for card in col]
            if all(v == values[0] for v in values):
                st.session_state.discard_pile.extend([card['value'] for card in col])
                continue
        new_grid.append(col)
    return new_grid

def reveal_random_card(grid):
    hidden = [(c, r) for c in range(len(grid)) for r in range(3) if not grid[c][r]['revealed']]
    if hidden:
        col, row = choice(hidden)
        grid[col][row]['revealed'] = True

def setup_new_round():
    full_deck = get_card_deck()
    shuffle(full_deck)
    st.session_state.draw_pile = full_deck[:-1]
    st.session_state.discard_pile = [full_deck[-1]]
    st.session_state.user_grid = init_grid(st.session_state.draw_pile)
    st.session_state.comp_grid = init_grid(st.session_state.draw_pile)
    st.session_state.selected_card = None
    st.session_state.turn = "user"
    st.session_state.final_turn = None
    for _ in range(2):
        reveal_random_card(st.session_state.user_grid)
        reveal_random_card(st.session_state.comp_grid)

def end_round():
    for col in st.session_state.user_grid:
        for card in col:
            card['revealed'] = True
    for col in st.session_state.comp_grid:
        for card in col:
            card['revealed'] = True
    st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid)
    st.session_state.comp_grid = remove_matching_columns(st.session_state.comp_grid)
    u_score = calculate_score(st.session_state.user_grid)
    c_score = calculate_score(st.session_state.comp_grid)
    st.session_state.user_total += u_score
    st.session_state.comp_total += c_score
    st.session_state.history.append({
        "Round": len(st.session_state.history) + 1,
        f"{st.session_state.player_name} Score": u_score,
        "Computer Score": c_score
    })
    if len(st.session_state.history) >= st.session_state.max_rounds:
        st.session_state.game_over = True

# --- Game Start ---
if "setup_complete" not in st.session_state:
    name = st.text_input("Enter your name:", value="Player")
    max_rounds = st.number_input("How many rounds to play?", 1, 20, 5)
    if st.button("Start Game") and name.strip():
        st.session_state.player_name = name
        st.session_state.user_total = 0
        st.session_state.comp_total = 0
        st.session_state.history = []
        st.session_state.max_rounds = max_rounds
        st.session_state.game_over = False
        st.session_state.setup_complete = True
        setup_new_round()
        st.rerun()
    st.stop()

# --- Turn Management ---
if st.session_state.game_over:
    st.header("🏁 Game Over")
    winner = st.session_state.player_name if st.session_state.user_total < st.session_state.comp_total else "Computer"
    st.success(f"Winner: {winner}")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
    if st.button("🔄 Restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.stop()

if all_revealed(st.session_state.user_grid):
    if st.session_state.final_turn is None:
        st.session_state.final_turn = "comp"
    elif st.session_state.final_turn == "user":
        end_round()
        setup_new_round()
        st.rerun()

if all_revealed(st.session_state.comp_grid):
    if st.session_state.final_turn is None:
        st.session_state.final_turn = "user"
    elif st.session_state.final_turn == "comp":
        end_round()
        setup_new_round()
        st.rerun()

# --- UI ---
st.markdown(f"### Turn: {'🟢 ' + st.session_state.player_name if st.session_state.turn == 'user' else '🤖 Computer'}")
st.markdown(f"📂 <b>{st.session_state.player_name} Points:</b> {count_revealed(st.session_state.user_grid)} / 12", unsafe_allow_html=True)
st.markdown(f"🧠 <b>Computer Points:</b> {count_revealed(st.session_state.comp_grid)} / 12", unsafe_allow_html=True)

button_col1, button_col2, button_col3 = st.columns([1,2,1])
if st.session_state.turn == "user" and st.session_state.selected_card is None:
    with button_col2:
        if st.button("🃏 Draw from pile"):
            st.session_state.selected_card = st.session_state.draw_pile.pop()
        top_discard = st.session_state.discard_pile[-1]
        st.markdown(f'<div style="text-align:center; margin-top:10px">Top Discard: <b>{top_discard}</b></div>', unsafe_allow_html=True)
        if st.button("📥 Take Discard"):
            st.session_state.selected_card = st.session_state.discard_pile.pop()

if st.session_state.selected_card is not None and st.session_state.turn == "user":
    st.markdown(f"<div style='background-color:{get_card_color(st.session_state.selected_card)}; padding:12px; text-align:center; border-radius:10px;'>Selected: {st.session_state.selected_card}</div>", unsafe_allow_html=True)
    if st.button("🗑 Discard it (Flip a card instead)"):
        st.session_state.discard_pile.append(st.session_state.selected_card)
        st.session_state.selected_card = None
        st.session_state.await_flip = True
    if st.session_state.get("await_flip"):
        st.info("Now click a ❓ to flip one card.")

def render_grid(grid, name, editable=False):
    st.markdown(f"#### {name}'s Grid")
    for r in range(3):
        row = st.columns(len(grid), gap='small')  # Ensure tight alignment
        for c in range(len(grid)):
            card = grid[c][r]
            key = f"{name}_{r}_{c}"
            if card['revealed']:
                color = get_card_color(card['value'])
                if editable and st.session_state.selected_card is not None:
                    if row[c].button(f"Swap ({card['value']})", key=key):
                        st.session_state.discard_pile.append(card['value'])
                        card['value'] = st.session_state.selected_card
                        card['revealed'] = True
                        st.session_state.selected_card = None
                        if name == st.session_state.player_name:
                            st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid)
                        else:
                            st.session_state.comp_grid = remove_matching_columns(st.session_state.comp_grid)
                        st.session_state.turn = "comp"
                        st.rerun()
                else:
                    row[c].markdown(f"<div style='display:flex; justify-content:center; align-items:center; height:100%;'>
<div style='background-color:{color};' class='card-style'>{card['value']}</div>", unsafe_allow_html=True)
            elif editable and st.session_state.selected_card is None:
                if row[c].button("❓", key=key):
                    card['revealed'] = True
                    st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid)
                    st.session_state.turn = "comp"
                    st.rerun()
            elif editable and st.session_state.selected_card is not None:
                if row[c].button("Swap", key=key):
                    st.session_state.discard_pile.append(card['value'])
                    card['value'] = st.session_state.selected_card
                    card['revealed'] = True
                    st.session_state.selected_card = None
                    st.session_state.user_grid = remove_matching_columns(st.session_state.user_grid)
                    st.session_state.turn = "comp"
                    st.rerun()
            else:
                row[c].markdown("❓")

button_col1, button_col2, button_col3 = st.columns([1,2,1])
with left:
    render_grid(st.session_state.user_grid, st.session_state.player_name, editable=(st.session_state.turn == "user"))

st.markdown("---")
with right:
    render_grid(st.session_state.comp_grid, "Computer")

if st.session_state.turn == "comp" and not st.session_state.game_over:
    time.sleep(1)
    action = choice(["draw", "discard"])
    if action == "discard" and st.session_state.discard_pile:
        picked = st.session_state.discard_pile.pop()
        col = choice(st.session_state.comp_grid)
        row = choice(col)
        st.session_state.discard_pile.append(row['value'])
        row['value'] = picked
        row['revealed'] = True
    else:
        drawn = st.session_state.draw_pile.pop()
        if choice([True, False]):
            col = choice(st.session_state.comp_grid)
            row = choice(col)
            st.session_state.discard_pile.append(row['value'])
            row['value'] = drawn
            row['revealed'] = True
        else:
            st.session_state.discard_pile.append(drawn)
            reveal_random_card(st.session_state.comp_grid)
    st.session_state.comp_grid = remove_matching_columns(st.session_state.comp_grid)
    st.session_state.turn = "user"
    st.rerun()



