import streamlit as st
import random
import copy
import time
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="🧩 Sudoku Game",
    page_icon="🧩",
    layout="wide"
)

# --- Initialize Session State ---
if 'board' not in st.session_state:
    st.session_state.board = None
if 'solution' not in st.session_state:
    st.session_state.solution = None
if 'initial_board' not in st.session_state:
    st.session_state.initial_board = None
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "Medium"
if 'game_completed' not in st.session_state:
    st.session_state.game_completed = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'hints_used' not in st.session_state:
    st.session_state.hints_used = 0
if 'mistakes' not in st.session_state:
    st.session_state.mistakes = 0

# --- Sudoku Helper Functions ---
def is_valid(board, row, col, num):
    """Check if placing num at (row, col) is valid"""
    # Check row
    for x in range(9):
        if board[row][x] == num:
            return False
    
    # Check column
    for x in range(9):
        if board[x][col] == num:
            return False
    
    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False
    
    return True

def solve_sudoku(board):
    """Solve sudoku using backtracking"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def generate_complete_board():
    """Generate a complete valid Sudoku board"""
    board = [[0 for _ in range(9)] for _ in range(9)]
    
    # Fill diagonal 3x3 boxes first
    for box in range(0, 9, 3):
        fill_box(board, box, box)
    
    # Solve the rest
    solve_sudoku(board)
    return board

def fill_box(board, row, col):
    """Fill a 3x3 box with random numbers"""
    nums = list(range(1, 10))
    random.shuffle(nums)
    
    for i in range(3):
        for j in range(3):
            board[row + i][col + j] = nums[i * 3 + j]

def remove_numbers(board, difficulty):
    """Remove numbers from board based on difficulty"""
    # Difficulty settings: (min_clues, max_clues)
    difficulty_settings = {
        "Easy": (45, 50),
        "Medium": (35, 44),
        "Hard": (25, 34)
    }
    
    min_clues, max_clues = difficulty_settings[difficulty]
    target_clues = random.randint(min_clues, max_clues)
    
    puzzle = copy.deepcopy(board)
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    
    removed = 0
    needed_to_remove = 81 - target_clues
    
    for row, col in cells:
        if removed >= needed_to_remove:
            break
            
        # Try removing this cell
        backup = puzzle[row][col]
        puzzle[row][col] = 0
        
        # Check if puzzle still has unique solution
        temp_board = copy.deepcopy(puzzle)
        if count_solutions(temp_board) == 1:
            removed += 1
        else:
            puzzle[row][col] = backup
    
    return puzzle

def count_solutions(board, limit=2):
    """Count number of solutions (up to limit)"""
    solutions = [0]
    
    def solve_count(board):
        if solutions[0] >= limit:
            return
            
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            solve_count(board)
                            board[row][col] = 0
                    return
        solutions[0] += 1
    
    solve_count(board)
    return solutions[0]

def generate_puzzle(difficulty):
    """Generate a new puzzle"""
    complete_board = generate_complete_board()
    puzzle = remove_numbers(complete_board, difficulty)
    return puzzle, complete_board

def is_board_complete(board):
    """Check if board is completely filled"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return False
    return True

def is_board_valid(board):
    """Check if current board state is valid"""
    for row in range(9):
        for col in range(9):
            if board[row][col] != 0:
                # Temporarily remove the number to check validity
                num = board[row][col]
                board[row][col] = 0
                if not is_valid(board, row, col, num):
                    board[row][col] = num
                    return False
                board[row][col] = num
    return True

def get_hint(board, solution):
    """Get a hint for the current board"""
    empty_cells = [(i, j) for i in range(9) for j in range(9) if board[i][j] == 0]
    if empty_cells:
        row, col = random.choice(empty_cells)
        return row, col, solution[row][col]
    return None

# --- Custom CSS for Sudoku Board ---
st.markdown("""
<style>
    .sudoku-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .sudoku-cell {
        width: 40px;
        height: 40px;
        border: 1px solid #333;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
    }
    .sudoku-cell-thick-right {
        border-right: 3px solid #000;
    }
    .sudoku-cell-thick-bottom {
        border-bottom: 3px solid #000;
    }
    .sudoku-cell-given {
        background-color: #f0f0f0;
        color: #000;
    }
    .sudoku-cell-user {
        background-color: #fff;
        color: #007bff;
    }
    .sudoku-cell-error {
        background-color: #ffebee;
        color: #d32f2f;
    }
    .sudoku-cell-hint {
        background-color: #e8f5e8;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# --- Main App ---
st.title("🧩 Sudoku Game")
st.markdown("Challenge yourself with different difficulty levels!")

# Sidebar for game controls
with st.sidebar:
    st.header("🎮 Game Controls")
    
    # Difficulty selection
    difficulty = st.selectbox(
        "Select Difficulty:",
        ["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
    )
    
    if difficulty != st.session_state.difficulty:
        st.session_state.difficulty = difficulty
    
    # New game button
    if st.button("🆕 New Game", type="primary", use_container_width=True):
        with st.spinner("Generating new puzzle..."):
            puzzle, solution = generate_puzzle(difficulty)
            st.session_state.board = copy.deepcopy(puzzle)
            st.session_state.solution = solution
            st.session_state.initial_board = copy.deepcopy(puzzle)
            st.session_state.game_completed = False
            st.session_state.start_time = time.time()
            st.session_state.hints_used = 0
            st.session_state.mistakes = 0
        st.success("New puzzle generated!")
        st.rerun()
    
    st.divider()
    
    # Game statistics
    if st.session_state.board is not None:
        st.header("📊 Game Stats")
        
        # Timer
        if st.session_state.start_time and not st.session_state.game_completed:
            elapsed_time = int(time.time() - st.session_state.start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            st.metric("⏱️ Time", f"{minutes:02d}:{seconds:02d}")
        
        # Other stats
        st.metric("💡 Hints Used", st.session_state.hints_used)
        st.metric("❌ Mistakes", st.session_state.mistakes)
        
        # Progress
        if st.session_state.board:
            filled_cells = sum(1 for row in st.session_state.board for cell in row if cell != 0)
            progress = (filled_cells / 81) * 100
            st.metric("📈 Progress", f"{progress:.1f}%")
    
    st.divider()
    
    # Game actions
    if st.session_state.board is not None and not st.session_state.game_completed:
        st.header("🔧 Actions")
        
        # Hint button
        if st.button("💡 Get Hint", use_container_width=True):
            hint = get_hint(st.session_state.board, st.session_state.solution)
            if hint:
                row, col, value = hint
                st.session_state.board[row][col] = value
                st.session_state.hints_used += 1
                st.success(f"Hint: Added {value} at row {row+1}, column {col+1}")
                st.rerun()
            else:
                st.info("No hints available - puzzle is complete!")
        
        # Validate button
        if st.button("✅ Check Solution", use_container_width=True):
            if is_board_valid(st.session_state.board):
                if is_board_complete(st.session_state.board):
                    st.session_state.game_completed = True
                    st.success("🎉 Congratulations! Puzzle completed!")
                    st.balloons()
                else:
                    st.info("✅ Looking good so far! Keep going!")
            else:
                st.error("❌ There are some errors in your solution")
        
        # Clear button
        if st.button("🗑️ Clear All", use_container_width=True):
            if st.checkbox("Are you sure?", key="clear_confirm"):
                st.session_state.board = copy.deepcopy(st.session_state.initial_board)
                st.session_state.mistakes = 0
                st.success("Board cleared!")
                st.rerun()

# Main game area
if st.session_state.board is None:
    st.info("👆 Select a difficulty and click 'New Game' to start playing!")
    
    # Instructions
    st.subheader("📋 How to Play Sudoku")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Objective:**
        Fill the 9×9 grid with numbers 1-9
        
        **📐 Rules:**
        • Each row must contain all digits 1-9
        • Each column must contain all digits 1-9
        • Each 3×3 box must contain all digits 1-9
        • No number can repeat in any row, column, or box
        """)
    
    with col2:
        st.markdown("""
        **🎮 Controls:**
        • Click on a cell to select it
        • Use the number input below the grid
        • Use hints sparingly for better scores
        • Check your solution anytime
        
        **🏆 Difficulty Levels:**
        • **Easy:** 45-50 given numbers
        • **Medium:** 35-44 given numbers  
        • **Hard:** 25-34 given numbers
        """)

else:
    # Display the Sudoku board
    st.subheader(f"🧩 Sudoku - {st.session_state.difficulty} Level")
    
    if st.session_state.game_completed:
        st.success("🎉 Puzzle Completed! Great job!")
        elapsed_time = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
        minutes, seconds = divmod(elapsed_time, 60)
        st.info(f"⏱️ Final Time: {minutes:02d}:{seconds:02d} | 💡 Hints: {st.session_state.hints_used} | ❌ Mistakes: {st.session_state.mistakes}")
    
    # Create input grid
    st.markdown("### Enter numbers in the cells:")
    
    # Create a 9x9 grid of number inputs
    board_changed = False
    
    for i in range(9):
        cols = st.columns(9)
        for j in range(9):
            with cols[j]:
                # Determine if this is a given number (unchangeable)
                is_given = st.session_state.initial_board[i][j] != 0
                
                if is_given:
                    # Display given numbers as disabled inputs
                    st.number_input(
                        f"",
                        min_value=1,
                        max_value=9,
                        value=st.session_state.board[i][j],
                        key=f"cell_{i}_{j}",
                        disabled=True,
                        label_visibility="collapsed"
                    )
                else:
                    # Allow user input for empty cells
                    current_value = st.session_state.board[i][j] if st.session_state.board[i][j] != 0 else None
                    
                    new_value = st.number_input(
                        f"",
                        min_value=1,
                        max_value=9,
                        value=current_value,
                        key=f"cell_{i}_{j}",
                        label_visibility="collapsed",
                        step=1
                    )
                    
                    # Update board if value changed
                    if new_value is not None:
                        if st.session_state.board[i][j] != new_value:
                            # Check if the move is valid
                            old_value = st.session_state.board[i][j]
                            st.session_state.board[i][j] = 0  # Temporarily clear
                            
                            if is_valid(st.session_state.board, i, j, new_value):
                                st.session_state.board[i][j] = new_value
                                board_changed = True
                            else:
                                st.session_state.board[i][j] = old_value
                                st.session_state.mistakes += 1
                                st.error(f"❌ Invalid move at row {i+1}, column {j+1}")
                    elif current_value is not None:
                        st.session_state.board[i][j] = 0
                        board_changed = True
    
    # Auto-check for completion
    if board_changed and is_board_complete(st.session_state.board):
        if is_board_valid(st.session_state.board):
            st.session_state.game_completed = True
            st.rerun()
    
    # Quick actions below the board
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💡 Quick Hint"):
            hint = get_hint(st.session_state.board, st.session_state.solution)
            if hint:
                row, col, value = hint
                st.session_state.board[row][col] = value
                st.session_state.hints_used += 1
                st.rerun()
    
    with col2:
        if st.button("✅ Validate"):
            if is_board_valid(st.session_state.board):
                st.success("✅ No errors found!")
            else:
                st.error("❌ Found errors!")
    
    with col3:
        if st.button("🔍 Show Solution"):
            if st.checkbox("Really show solution?", key="show_solution"):
                st.session_state.board = copy.deepcopy(st.session_state.solution)
                st.session_state.game_completed = True
                st.info("Solution revealed!")
                st.rerun()
    
    with col4:
        if st.button("↩️ Reset"):
            st.session_state.board = copy.deepcopy(st.session_state.initial_board)
            st.session_state.mistakes = 0
            st.success("Board reset!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>🧩 **Sudoku Game** - Challenge your mind with logic puzzles!</small>
</div>
""", unsafe_allow_html=True)
