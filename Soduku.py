import streamlit as st
import random
import copy
import time

# --- Page Config ---
st.set_page_config(
    page_title="🧩 Sudoku Game",
    page_icon="🧩",
    layout="centered"
)

# --- Initialize Session State ---
def init_session_state():
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
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None
    if 'first_load' not in st.session_state:
        st.session_state.first_load = True

init_session_state()

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

def generate_simple_puzzle(difficulty):
    """Generate a simple valid puzzle"""
    # Start with a pre-made solution for speed
    base_solution = [
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9]
    ]
    
    # Shuffle to create variation
    solution = copy.deepcopy(base_solution)
    
    # Random row swaps within boxes
    for box_start in [0, 3, 6]:
        rows = list(range(box_start, box_start + 3))
        random.shuffle(rows)
        original_rows = [solution[i] for i in range(box_start, box_start + 3)]
        for i, new_row_idx in enumerate(rows):
            solution[box_start + i] = original_rows[new_row_idx - box_start]
    
    # Random column swaps within boxes
    for box_start in [0, 3, 6]:
        cols = list(range(box_start, box_start + 3))
        random.shuffle(cols)
        
        # Create new solution with swapped columns
        new_solution = [[0 for _ in range(9)] for _ in range(9)]
        for row in range(9):
            for i, col_idx in enumerate(cols):
                new_solution[row][box_start + i] = solution[row][col_idx]
        solution = new_solution
    
    # Remove numbers based on difficulty
    puzzle = copy.deepcopy(solution)
    
    # Difficulty settings
    cells_to_remove = {
        "Easy": 35,      # Remove 35 numbers (46 given)
        "Medium": 45,    # Remove 45 numbers (36 given)  
        "Hard": 55       # Remove 55 numbers (26 given)
    }
    
    remove_count = cells_to_remove[difficulty]
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    
    for i in range(remove_count):
        if i < len(cells):
            row, col = cells[i]
            puzzle[row][col] = 0
    
    return puzzle, solution

def display_sudoku_board():
    """Display the Sudoku board with clickable interface"""
    st.markdown("### 🎯 Click a cell and enter a number (1-9)")
    
    # Create grid display
    board_html = '<div style="display: flex; justify-content: center; margin: 20px 0;">'
    board_html += '<table style="border-collapse: collapse; border: 3px solid #000;">'
    
    for i in range(9):
        board_html += '<tr>'
        for j in range(9):
            # Cell styling
            cell_style = "width: 40px; height: 40px; text-align: center; font-size: 18px; font-weight: bold; border: 1px solid #666;"
            
            # Thick borders for 3x3 boxes
            if j % 3 == 2 and j != 8:
                cell_style += " border-right: 3px solid #000;"
            if i % 3 == 2 and i != 8:
                cell_style += " border-bottom: 3px solid #000;"
            
            # Color coding
            value = st.session_state.board[i][j]
            is_given = st.session_state.initial_board[i][j] != 0
            
            if is_given:
                cell_style += " background-color: #f5f5f5; color: #000;"
            elif value != 0:
                cell_style += " background-color: #e3f2fd; color: #1976d2;"
            else:
                cell_style += " background-color: #fff;"
            
            # Cell content
            display_value = str(value) if value != 0 else ""
            
            board_html += f'<td style="{cell_style}">{display_value}</td>'
        
        board_html += '</tr>'
    
    board_html += '</table></div>'
    
    st.markdown(board_html, unsafe_allow_html=True)

# --- Main App ---
st.title("🧩 Sudoku Game")

# Auto-generate first puzzle
if st.session_state.first_load:
    with st.spinner("Generating your first puzzle..."):
        puzzle, solution = generate_simple_puzzle("Medium")
        st.session_state.board = copy.deepcopy(puzzle)
        st.session_state.solution = solution
        st.session_state.initial_board = copy.deepcopy(puzzle)
        st.session_state.start_time = time.time()
        st.session_state.first_load = False
    st.success("Welcome! Your puzzle is ready!")

# Game controls
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Difficulty and new game
    difficulty = st.selectbox(
        "🎯 Select Difficulty:",
        ["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
    )
    
    if st.button("🆕 New Game", type="primary", use_container_width=True):
        with st.spinner(f"Generating {difficulty} puzzle..."):
            puzzle, solution = generate_simple_puzzle(difficulty)
            st.session_state.board = copy.deepcopy(puzzle)
            st.session_state.solution = solution
            st.session_state.initial_board = copy.deepcopy(puzzle)
            st.session_state.difficulty = difficulty
            st.session_state.game_completed = False
            st.session_state.start_time = time.time()
            st.session_state.hints_used = 0
        st.success(f"New {difficulty} puzzle generated!")
        st.rerun()

# Display current game status
if st.session_state.board is not None:
    if st.session_state.game_completed:
        st.success("🎉 Congratulations! Puzzle Completed!")
        st.balloons()
    
    # Game stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filled = sum(1 for row in st.session_state.board for cell in row if cell != 0)
        st.metric("Progress", f"{filled}/81")
    
    with col2:
        if st.session_state.start_time:
            elapsed = int(time.time() - st.session_state.start_time)
            mins, secs = divmod(elapsed, 60)
            st.metric("Time", f"{mins:02d}:{secs:02d}")
    
    with col3:
        st.metric("Hints", st.session_state.hints_used)
    
    with col4:
        st.metric("Level", st.session_state.difficulty)
    
    # Display the board
    display_sudoku_board()
    
    # Cell selection and input
    st.markdown("### 🎯 Select Cell and Enter Number")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_row = st.selectbox("Row (1-9):", range(1, 10), index=0) - 1
        selected_col = st.selectbox("Column (1-9):", range(1, 10), index=0) - 1
    
    with col2:
        # Check if selected cell is modifiable
        is_given = st.session_state.initial_board[selected_row][selected_col] != 0
        
        if is_given:
            st.info(f"Cell ({selected_row+1}, {selected_col+1}) is given and cannot be changed")
            current_value = st.session_state.board[selected_row][selected_col]
            st.write(f"**Value: {current_value}**")
        else:
            current_value = st.session_state.board[selected_row][selected_col] if st.session_state.board[selected_row][selected_col] != 0 else None
            
            new_value = st.number_input(
                f"Enter number for cell ({selected_row+1}, {selected_col+1}):",
                min_value=1,
                max_value=9,
                value=current_value,
                step=1,
                key="number_input"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✅ Place Number", use_container_width=True):
                    if new_value is not None:
                        # Temporarily clear cell to check validity
                        old_value = st.session_state.board[selected_row][selected_col]
                        st.session_state.board[selected_row][selected_col] = 0
                        
                        if is_valid(st.session_state.board, selected_row, selected_col, new_value):
                            st.session_state.board[selected_row][selected_col] = new_value
                            st.success(f"✅ Placed {new_value} at ({selected_row+1}, {selected_col+1})")
                            
                            # Check if puzzle is complete
                            if all(st.session_state.board[r][c] != 0 for r in range(9) for c in range(9)):
                                st.session_state.game_completed = True
                                st.rerun()
                        else:
                            st.session_state.board[selected_row][selected_col] = old_value
                            st.error(f"❌ Invalid! {new_value} conflicts with row, column, or box rules")
            
            with col_b:
                if st.button("🗑️ Clear Cell", use_container_width=True):
                    st.session_state.board[selected_row][selected_col] = 0
                    st.success(f"✅ Cleared cell ({selected_row+1}, {selected_col+1})")
    
    st.divider()
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💡 Hint", use_container_width=True):
            # Find an empty cell and fill it
            empty_cells = [(i, j) for i in range(9) for j in range(9) 
                          if st.session_state.board[i][j] == 0]
            if empty_cells:
                row, col = random.choice(empty_cells)
                correct_value = st.session_state.solution[row][col]
                st.session_state.board[row][col] = correct_value
                st.session_state.hints_used += 1
                st.success(f"💡 Hint: Placed {correct_value} at ({row+1}, {col+1})")
                st.rerun()
            else:
                st.info("No empty cells for hints!")
    
    with col2:
        if st.button("✅ Check", use_container_width=True):
            # Check current state
            errors = 0
            for i in range(9):
                for j in range(9):
                    if st.session_state.board[i][j] != 0:
                        num = st.session_state.board[i][j]
                        st.session_state.board[i][j] = 0
                        if not is_valid(st.session_state.board, i, j, num):
                            errors += 1
                        st.session_state.board[i][j] = num
            
            if errors == 0:
                if all(st.session_state.board[r][c] != 0 for r in range(9) for c in range(9)):
                    st.success("🎉 Perfect! Puzzle completed!")
                    st.session_state.game_completed = True
                else:
                    st.success("✅ No errors so far!")
            else:
                st.error(f"❌ Found {errors} error(s)")
    
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.board = copy.deepcopy(st.session_state.initial_board)
            st.session_state.game_completed = False
            st.session_state.hints_used = 0
            st.success("🔄 Board reset!")
            st.rerun()
    
    with col4:
        if st.button("💯 Solve", use_container_width=True):
            if st.checkbox("Show solution?"):
                st.session_state.board = copy.deepcopy(st.session_state.solution)
                st.session_state.game_completed = True
                st.info("Solution revealed!")
                st.rerun()

# Auto-generate puzzle if none exists
if st.session_state.board is None:
    with st.spinner("Loading your puzzle..."):
        puzzle, solution = generate_simple_puzzle(st.session_state.difficulty)
        st.session_state.board = copy.deepcopy(puzzle)
        st.session_state.solution = solution
        st.session_state.initial_board = copy.deepcopy(puzzle)
        st.session_state.start_time = time.time()
    st.rerun()

# Footer with instructions
st.markdown("---")
with st.expander("📋 How to Play"):
    st.markdown("""
    **🎯 Goal:** Fill the 9×9 grid with numbers 1-9
    
    **📐 Rules:**
    - Each row must have all numbers 1-9
    - Each column must have all numbers 1-9  
    - Each 3×3 box must have all numbers 1-9
    - No repeating numbers in any row, column, or box
    
    **🎮 How to play:**
    1. Select a cell using the Row/Column dropdowns
    2. Enter a number (1-9) 
    3. Click "Place Number" to confirm
    4. Use hints if you get stuck
    5. Check your progress anytime
    
    **🏆 Difficulty:**
    - **Easy:** More given numbers (easier start)
    - **Medium:** Moderate challenge
    - **Hard:** Fewer given numbers (harder puzzle)
    """)

st.markdown("""
<div style="text-align: center; color: #666; margin-top: 20px;">
    <small>🧩 <strong>Quick Tip:</strong> Look for cells where only one number can fit!</small>
</div>
""", unsafe_allow_html=True)
