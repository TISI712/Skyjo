import streamlit as st
from random import shuffle, choice
import time
import pandas as pd

# --- Setup Streamlit Page ---
st.set_page_config(layout="wide")

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
    st.session_state.player_name = st.text_input("Enter your name:", value="Player")
    st.session_state.target_score = st.number_input("Game ends when someone reaches this score:", min_value=50, max_value=200, value=100)
    if st.button("Start Game") and st.session_state.player_name.strip():
        st.session_state.user_total = 0
        st.session_state.comp_total = 0
        st.session_state.round_starter = None
        st.session_state.message_log = []
        st.session_state.history = []
        setup_new_round()
        st.session_state.setup_complete = True
        st.rerun()
    st.stop()

# --- Round End Check ---
if all_revealed(st.session_state.user_grid) or all_revealed(st.session_state.comp_grid):
    st.session_state.game_over = True
    st.subheader("✅ Round Finished")

    user_score = calculate_score(st.session_state.user_grid)
    comp_score = calculate_score(st.session_state.comp_grid)

    if st.session_state.round_starter == "user" and user_score > comp_score:
        user_score *= 2
        st.warning("You ended the round but did NOT win – your score is doubled!")
    elif st.session_state.round_starter == "comp" and comp_score > user_score:
        comp_score *= 2
        st.info("Computer ended the round but did NOT win – its score is doubled!")

    st.session_state.user_total += user_score
    st.session_state.comp_total += comp_score

    round_data = {
        "Round": len(st.session_state.history) + 1,
        f"{st.session_state.player_name} Score": user_score,
        "Computer Score": comp_score,
        "Winner": st.session_state.player_name if user_score < comp_score else ("Computer" if comp_score < user_score else "Tie")
    }
    st.session_state.history.append(round_data)

    st.success(f"Your round score: {user_score} | Computer: {comp_score}")
    st.info(f"🏁 Total – {st.session_state.player_name}: {st.session_state.user_total} | Computer: {st.session_state.comp_total}")

    if st.session_state.history:
        st.markdown("### 📊 Round History")
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Score History", data=csv, file_name="skyjo_scores.csv", mime="text/csv")

    if st.session_state.user_total >= st.session_state.target_score or st.session_state.comp_total >= st.session_state.target_score:
        winner = st.session_state.player_name if st.session_state.user_total < st.session_state.comp_total else "Computer"
        st.error(f"🎉 Game Over – {winner} wins!")
        if st.button("🕹 Play Again"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    elif st.button("▶️ Start New Round"):
        setup_new_round()
        st.rerun()
        
