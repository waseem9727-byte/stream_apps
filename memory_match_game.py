import streamlit as st
import random
import time
from datetime import datetime

# Configure the page for mobile-friendly display
st.set_page_config(
    page_title="🧠 Memory Match",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add PWA-like meta tags and mobile optimization
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Memory Match">
<meta name="theme-color" content="#9C27B0">

<style>
/* Mobile-first responsive design */
.main > div {
    padding-top: 0.5rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

.stButton > button {
    width: 100%;
    height: 3rem;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 15px;
    margin: 0.3rem 0;
    transition: all 0.3s ease;
}

/* Game board styling */
.game-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    max-width: 350px;
    margin: 0 auto;
    padding: 10px;
}

.card {
    aspect-ratio: 1;
    border: 3px solid #ddd;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 60px;
}

.card.hidden {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: transparent;
}

.card.revealed {
    background: white;
    transform: scale(1.05);
    border-color: #4CAF50;
}

.card.matched {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    border-color: #4CAF50;
    transform: scale(0.95);
}

.card.wrong {
    background: linear-gradient(135deg, #f44336, #d32f2f);
    color: white;
    border-color: #f44336;
    animation: shake 0.5s;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

/* Game header */
.game-header {
    text-align: center;
    padding: 1rem 0 0.5rem 0;
}

.stats-container {
    background: linear-gradient(90deg, #9C27B0, #E91E63);
    color: white;
    padding: 1rem;
    border-radius: 15px;
    text-align: center;
    margin: 1rem 0;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    display: block;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

.difficulty-selector {
    text-align: center;
    margin: 1rem 0;
}

.game-controls {
    text-align: center;
    margin: 1rem 0;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Success message */
.success-message {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    margin: 1rem 0;
    font-size: 1.2rem;
    animation: bounce 1s ease-in-out;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}
</style>
""", unsafe_allow_html=True)

# Game emojis for cards
EMOJI_SETS = {
    'easy': ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼'],
    'medium': ['🍎', '🍊', '🍋', '🍌', '🍇', '🍓', '🥝', '🍑', '🥭', '🍍'],
    'hard': ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥅', '⛳']
}

# Initialize session state
def init_game_state():
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = 'easy'
    if 'board_size' not in st.session_state:
        st.session_state.board_size = {'easy': 4, 'medium': 5, 'hard': 6}
    if 'game_board' not in st.session_state:
        st.session_state.game_board = []
    if 'revealed_cards' not in st.session_state:
        st.session_state.revealed_cards = []
    if 'matched_pairs' not in st.session_state:
        st.session_state.matched_pairs = set()
    if 'moves' not in st.session_state:
        st.session_state.moves = 0
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'game_won' not in st.session_state:
        st.session_state.game_won = False
    if 'best_times' not in st.session_state:
        st.session_state.best_times = {'easy': None, 'medium': None, 'hard': None}
    if 'games_completed' not in st.session_state:
        st.session_state.games_completed = {'easy': 0, 'medium': 0, 'hard': 0}

def create_game_board(difficulty):
    """Create a shuffled game board based on difficulty"""
    size = st.session_state.board_size[difficulty]
    total_cards = size * size
    pairs_needed = total_cards // 2
    
    emojis = EMOJI_SETS[difficulty][:pairs_needed]
    board = emojis * 2  # Create pairs
    random.shuffle(board)
    
    return board

def reset_game():
    """Reset the game state"""
    st.session_state.game_board = create_game_board(st.session_state.difficulty)
    st.session_state.revealed_cards = []
    st.session_state.matched_pairs = set()
    st.session_state.moves = 0
    st.session_state.game_started = True
    st.session_state.start_time = time.time()
    st.session_state.game_won = False

def handle_card_click(index):
    """Handle card click logic"""
    if not st.session_state.game_started or st.session_state.game_won:
        return
    
    if index in st.session_state.revealed_cards or index in st.session_state.matched_pairs:
        return
    
    st.session_state.revealed_cards.append(index)
    
    if len(st.session_state.revealed_cards) == 2:
        st.session_state.moves += 1
        card1_idx, card2_idx = st.session_state.revealed_cards
        
        if st.session_state.game_board[card1_idx] == st.session_state.game_board[card2_idx]:
            # Match found
            st.session_state.matched_pairs.add(card1_idx)
            st.session_state.matched_pairs.add(card2_idx)
            st.session_state.revealed_cards = []
            
            # Check if game is won
            if len(st.session_state.matched_pairs) == len(st.session_state.game_board):
                st.session_state.game_won = True
                end_time = time.time()
                game_time = end_time - st.session_state.start_time
                
                # Update best time
                current_best = st.session_state.best_times[st.session_state.difficulty]
                if current_best is None or game_time < current_best:
                    st.session_state.best_times[st.session_state.difficulty] = game_time
                
                st.session_state.games_completed[st.session_state.difficulty] += 1
        else:
            # No match - cards will be hidden after a delay
            time.sleep(0.5)
            st.session_state.revealed_cards = []

# Initialize game
init_game_state()

# Game header
st.markdown("""
<div class="game-header">
    <h1>🧠 Memory Match</h1>
    <p>Find all the matching pairs!</p>
</div>
""", unsafe_allow_html=True)

# Difficulty selector
col1, col2, col3 = st.columns(3)
with col2:
    new_difficulty = st.selectbox(
        "Difficulty:",
        options=['easy', 'medium', 'hard'],
        index=['easy', 'medium', 'hard'].index(st.session_state.difficulty),
        format_func=lambda x: f"{x.title()} ({st.session_state.board_size[x]}x{st.session_state.board_size[x]})"
    )
    
    if new_difficulty != st.session_state.difficulty:
        st.session_state.difficulty = new_difficulty
        st.session_state.game_started = False

# Game statistics
if st.session_state.game_started:
    elapsed_time = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
    elapsed_mins = elapsed_time // 60
    elapsed_secs = elapsed_time % 60
    time_display = f"{elapsed_mins}:{elapsed_secs:02d}"
else:
    time_display = "0:00"

best_time = st.session_state.best_times[st.session_state.difficulty]
best_time_display = f"{int(best_time//60)}:{int(best_time%60):02d}" if best_time else "None"

st.markdown(f"""
<div class="stats-container">
    <div class="stat-item">
        <span class="stat-value">{st.session_state.moves}</span>
        <span class="stat-label">Moves</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{time_display}</span>
        <span class="stat-label">Time</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{best_time_display}</span>
        <span class="stat-label">Best Time</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Game controls
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.game_started:
        if st.button("🎮 Start Game", key="start_game"):
            reset_game()
            st.rerun()
    else:
        if st.button("🔄 New Game", key="new_game"):
            reset_game()
            st.rerun()

# Game board
if st.session_state.game_started:
    if st.session_state.game_won:
        game_time = time.time() - st.session_state.start_time
        st.markdown(f"""
        <div class="success-message">
            🎉 Congratulations! You won!<br>
            ⏱️ Time: {int(game_time//60)}:{int(game_time%60):02d}<br>
            🎯 Moves: {st.session_state.moves}
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    
    # Create game grid
    size = st.session_state.board_size[st.session_state.difficulty]
    
    # Custom CSS for current board size
    st.markdown(f"""
    <style>
    .current-game-grid {{
        display: grid;
        grid-template-columns: repeat({size}, 1fr);
        gap: 6px;
        max-width: {min(350, 80 * size)}px;
        margin: 1rem auto;
        padding: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Create interactive game grid with clickable cards
    cols = st.columns(size)
    for i, emoji in enumerate(st.session_state.game_board):
        col_idx = i % size
        row_idx = i // size
        
        with cols[col_idx]:
            # Determine card state and appearance
            if i in st.session_state.matched_pairs:
                # Matched card - show emoji with green background
                card_emoji = emoji
                button_style = """
                    background: linear-gradient(135deg, #4CAF50, #45a049) !important;
                    color: white !important;
                    border: 3px solid #4CAF50 !important;
                    font-size: 2rem !important;
                    height: 70px !important;
                    border-radius: 12px !important;
                    transform: scale(0.95);
                """
            elif i in st.session_state.revealed_cards:
                # Currently revealed card - show emoji with highlight
                card_emoji = emoji
                button_style = """
                    background: white !important;
                    color: #333 !important;
                    border: 3px solid #4CAF50 !important;
                    font-size: 2rem !important;
                    height: 70px !important;
                    border-radius: 12px !important;
                    transform: scale(1.05);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                """
            else:
                # Hidden card - show question mark
                card_emoji = "❓"
                button_style = """
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white !important;
                    border: 3px solid #ddd !important;
                    font-size: 2rem !important;
                    height: 70px !important;
                    border-radius: 12px !important;
                    transition: all 0.3s ease !important;
                """
            
            # Create clickable card button
            st.markdown(f"""
                <style>
                .card-button-{i} > button {{
                    {button_style}
                    width: 100% !important;
                }}
                .card-button-{i} > button:hover {{
                    transform: scale(1.02) !important;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
                }}
                </style>
            """, unsafe_allow_html=True)
            
            # Only make card clickable if it's not matched and not already revealed (unless we need to hide it)
            if (i not in st.session_state.matched_pairs and 
                (i not in st.session_state.revealed_cards or len(st.session_state.revealed_cards) < 2)):
                
                if st.button(
                    card_emoji, 
                    key=f"card_{i}",
                    help=f"Card {i+1}",
                    disabled=st.session_state.game_won
                ):
                    handle_card_click(i)
                    st.rerun()
                    
                # Apply custom styling to this specific button
                st.markdown(f'<div class="card-button-{i}"></div>', unsafe_allow_html=True)
            else:
                # For matched cards or revealed cards waiting to be hidden, show as disabled
                st.button(
                    card_emoji, 
                    key=f"card_disabled_{i}",
                    disabled=True
                )
                st.markdown(f'<div class="card-button-{i}"></div>', unsafe_allow_html=True)

# Game statistics summary
st.markdown("---")
total_games = sum(st.session_state.games_completed.values())
st.markdown(f"""
<div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
    <h3>🏆 Your Stats</h3>
    <p><strong>Games Completed:</strong> {total_games}</p>
    <p><strong>Easy:</strong> {st.session_state.games_completed['easy']} | 
    <strong>Medium:</strong> {st.session_state.games_completed['medium']} | 
    <strong>Hard:</strong> {st.session_state.games_completed['hard']}</p>
</div>
""", unsafe_allow_html=True)

# Instructions
with st.expander("📖 How to Play"):
    st.write("""
    **Game Rules:**
    - Click cards to reveal them
    - Find matching pairs of emojis
    - Remember the positions of revealed cards
    - Match all pairs to win!
    
    **Difficulty Levels:**
    - **Easy:** 4x4 grid (8 pairs)
    - **Medium:** 5x5 grid (12 pairs) 
    - **Hard:** 6x6 grid (18 pairs)
    
    **Scoring:**
    - Fewer moves = better score
    - Faster time = better score
    - Try to beat your best times!
    
    **Mobile Tips:**
    - Add to home screen for app-like experience
    - Works great in portrait mode
    - Tap cards to reveal them
    """)

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    🧠 <strong>Memory Match Game</strong> - Challenge your memory!<br>
    Add to home screen for the best mobile experience
</div>
""", unsafe_allow_html=True)
