import streamlit as st
import random
import time

# Configure the page for mobile-friendly display
st.set_page_config(
    page_title="🎯 Guess the Number",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add PWA-like meta tags and mobile optimization
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Guess the Number">
<meta name="theme-color" content="#FF6B6B">

<style>
/* Mobile-first responsive design */
.main > div {
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.stButton > button {
    width: 100%;
    height: 3rem;
    font-size: 1.2rem;
    font-weight: bold;
    border-radius: 10px;
    margin: 0.5rem 0;
}

.stNumberInput > div > div > input {
    font-size: 1.5rem;
    text-align: center;
    height: 3rem;
}

/* Game UI styling */
.game-header {
    text-align: center;
    padding: 1rem 0;
}

.score-display {
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
    font-size: 1.1rem;
}

.feedback {
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    font-size: 1.2rem;
    margin: 1rem 0;
}

.feedback.correct {
    background-color: #D4EDDA;
    color: #155724;
    border: 2px solid #C3E6CB;
}

.feedback.too-high {
    background-color: #F8D7DA;
    color: #721C24;
    border: 2px solid #F5C6CB;
}

.feedback.too-low {
    background-color: #FFF3CD;
    color: #856404;
    border: 2px solid #FFEAA7;
}

/* Hide Streamlit elements for cleaner mobile experience */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'target_number' not in st.session_state:
    st.session_state.target_number = random.randint(1, 100)
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'max_attempts' not in st.session_state:
    st.session_state.max_attempts = 7
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'won' not in st.session_state:
    st.session_state.won = False
if 'high_score' not in st.session_state:
    st.session_state.high_score = float('inf')
if 'games_played' not in st.session_state:
    st.session_state.games_played = 0

# Game header
st.markdown("""
<div class="game-header">
    <h1>🎯 Guess the Number!</h1>
    <p>I'm thinking of a number between 1 and 100</p>
</div>
""", unsafe_allow_html=True)

# Score display
attempts_left = st.session_state.max_attempts - st.session_state.attempts
high_score_text = f"{st.session_state.high_score}" if st.session_state.high_score != float('inf') else "None"

st.markdown(f"""
<div class="score-display">
    <strong>Attempts Left:</strong> {attempts_left} | 
    <strong>Games Played:</strong> {st.session_state.games_played} | 
    <strong>Best Score:</strong> {high_score_text}
</div>
""", unsafe_allow_html=True)

# Main game logic
if not st.session_state.game_over:
    # Input for guess
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        guess = st.number_input(
            "Enter your guess:",
            min_value=1,
            max_value=100,
            value=50,
            step=1,
            key="guess_input"
        )
        
        if st.button("🎲 Make Guess", key="guess_button"):
            st.session_state.attempts += 1
            
            if guess == st.session_state.target_number:
                st.session_state.won = True
                st.session_state.game_over = True
                st.session_state.games_played += 1
                
                # Update high score
                if st.session_state.attempts < st.session_state.high_score:
                    st.session_state.high_score = st.session_state.attempts
                
                st.markdown(f"""
                <div class="feedback correct">
                    🎉 Congratulations! You guessed it in {st.session_state.attempts} attempts!
                </div>
                """, unsafe_allow_html=True)
                
                # Celebration effect
                st.balloons()
                
            elif st.session_state.attempts >= st.session_state.max_attempts:
                st.session_state.game_over = True
                st.session_state.games_played += 1
                st.markdown(f"""
                <div class="feedback too-high">
                    😔 Game Over! The number was {st.session_state.target_number}
                </div>
                """, unsafe_allow_html=True)
                
            elif guess > st.session_state.target_number:
                st.markdown("""
                <div class="feedback too-high">
                    📉 Too high! Try a lower number.
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.markdown("""
                <div class="feedback too-low">
                    📈 Too low! Try a higher number.
                </div>
                """, unsafe_allow_html=True)

# Game over state
if st.session_state.game_over:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Play Again", key="new_game"):
            # Reset game state
            st.session_state.target_number = random.randint(1, 100)
            st.session_state.attempts = 0
            st.session_state.game_over = False
            st.session_state.won = False
            st.rerun()

# Game instructions
with st.expander("📖 How to Play"):
    st.write("""
    **Rules:**
    - I'm thinking of a number between 1 and 100
    - You have 7 attempts to guess it
    - After each guess, I'll tell you if you need to go higher or lower
    - Try to guess it in as few attempts as possible!
    
    **Adding to Home Screen:**
    - **Android Chrome:** Tap the menu (⋮) → "Add to Home screen"
    - **iOS Safari:** Tap Share → "Add to Home Screen"
    """)

# Footer with tips for mobile users
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    💡 <strong>Tip:</strong> Add this game to your home screen for quick access!<br>
    Tap your browser menu and select "Add to Home Screen"
</div>
""", unsafe_allow_html=True)
