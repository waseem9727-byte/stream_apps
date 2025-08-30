import streamlit as st
import random
import string
import time
from typing import List, Tuple

# ----------------------------
# Word List (expandable)
# ----------------------------
WORDS = ["apple", "grape", "mango", "peach", "berry", "melon", "lemon", "chili", "guava"]

# ----------------------------
# Helper Functions
# ----------------------------
def new_secret_word() -> str:
    return random.choice(WORDS).upper()

def check_guess(secret: str, guess: str) -> List[str]:
    feedback = []
    for i, ch in enumerate(guess):
        if ch == secret[i]:
            feedback.append("🟩")
        elif ch in secret:
            feedback.append("🟨")
        else:
            feedback.append("⬜")
    return feedback

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Mini Word Game", page_icon="🎮", layout="centered")
st.title("🎮 Mobile Word Game")

if "secret" not in st.session_state:
    st.session_state.secret = new_secret_word()
    st.session_state.history = []
    st.session_state.game_over = False

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 New Game"):
        st.session_state.secret = new_secret_word()
        st.session_state.history = []
        st.session_state.game_over = False
        st.success("New game started!")

with col2:
    if st.button("❌ Reveal"):
        st.info(f"The secret word was: **{st.session_state.secret}**")
        st.session_state.game_over = True

# Guess Input
guess = st.text_input("Enter your guess (5 letters):", max_chars=5).upper()

if st.button("Submit Guess") and not st.session_state.game_over:
    if len(guess) != 5:
        st.warning("Please enter a 5-letter word!")
    else:
        result = check_guess(st.session_state.secret, guess)
        st.session_state.history.append((guess, "".join(result)))
        if guess == st.session_state.secret:
            st.success("🎉 Correct! You guessed it!")
            st.session_state.game_over = True

# Display history
st.subheader("Your Guesses")
for g, fb in st.session_state.history:
    st.write(f"{g} → {fb}")

