import streamlit as st
import random
from typing import List

# ----------------------------
# Game Configuration
# ----------------------------
WORDS = ["APPLE", "MANGO", "GRAPE", "BERRY", "PEACH", "LEMON", "PLUM", "PEAR"]

# ----------------------------
# Helper Functions
# ----------------------------
def check_guess(secret: str, guess: str) -> List[str]:
    """Compare guess with secret word and return feedback list."""
    feedback = ["⬜"] * len(secret)  # Default to gray
    secret_letters = list(secret)

    # Mark greens (correct position)
    for i in range(len(secret)):
        if guess[i] == secret[i]:
            feedback[i] = "🟩"
            secret_letters[i] = None  # mark as used

    # Mark yellows (wrong position but correct letter)
    for i in range(len(secret)):
        if feedback[i] == "⬜" and guess[i] in secret_letters:
            feedback[i] = "🟨"
            secret_letters[secret_letters.index(guess[i])] = None

    return feedback

# ----------------------------
# Initialize Session State
# ----------------------------
if "secret" not in st.session_state:
    st.session_state.secret = random.choice(WORDS)
if "history" not in st.session_state:
    st.session_state.history = []
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# ----------------------------
# UI
# ----------------------------
st.title("🎮 Word Guess Game")
st.write("Guess the hidden fruit name. Feedback: 🟩 correct, 🟨 wrong place, ⬜ not present.")

# Show available words
st.subheader("Available Words")
st.write(", ".join(WORDS))

# Guess input via dropdown
guess = st.selectbox("Pick your guess:", [""] + WORDS)

# Submit guess
if st.button("Submit Guess") and not st.session_state.game_over:
    if guess == "":
        st.warning("Please select a word!")
    else:
        result = check_guess(st.session_state.secret, guess)
        st.session_state.history.append((guess, "".join(result)))

        if guess == st.session_state.secret:
            st.success("🎉 Correct! You guessed it!")
            st.session_state.game_over = True

# Show history
if st.session_state.history:
    st.subheader("Your Guesses")
    for g, r in st.session_state.history:
        st.write(f"{g} → {r}")

# Restart button
if st.button("🔄 Restart Game"):
    st.session_state.secret = random.choice(WORDS)
    st.session_state.history = []
    st.session_state.game_over = False
    st.info("New game started! Pick a word from the list above.")
