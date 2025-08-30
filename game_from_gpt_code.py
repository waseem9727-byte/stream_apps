app.py

""" Wordly: A Wordle-style game built with Streamlit (mobile-friendly)

How to run locally:

1. Install Python 3.9+ and run:  pip install streamlit


2. Save this file as app.py in your repo, then run:  streamlit run app.py


3. On your phone (same Wi‑Fi), open the URL shown in the terminal (e.g., http://<your-ip>:8501). If needed, start with: streamlit run app.py --server.address 0.0.0.0 --server.port 8501



Gameplay:

You have 6 attempts to guess a 5-letter word.

Tap the on-screen keyboard to enter letters, ⌫ to delete, and Enter to submit.

Colors: Green = correct letter & spot, Yellow = correct letter wrong spot, Gray = not in word. """


import random import string import time from typing import List, Tuple

import streamlit as st

---------------------- Page Config & Minimal CSS ----------------------

st.set_page_config(page_title="Wordly • Streamlit", page_icon="🧩", layout="centered")

MOBILE_CSS = """

<style>
/**** Layout tweaks for mobile ****/
.block-container { padding-top: 1rem; padding-bottom: 2rem; }
.word-grid { display: grid; grid-template-columns: repeat(5, 3.2rem); grid-gap: 0.5rem; justify-content: center; }
.tile { height: 3.2rem; width: 3.2rem; display: flex; align-items: center; justify-content: center; border-radius: 0.5rem; font-weight: 800; font-size: 1.25rem; text-transform: uppercase; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }
.tile-empty { border: 2px solid #d0d7de; background: #f8fafc; color: #0f172a; }
.tile-absent { background: #a3a3a3; color: white; }
.tile-present { background: #eab308; color: #111827; }
.tile-correct { background: #22c55e; color: white; }
.row { display: grid; grid-template-columns: repeat(5, 3.2rem); grid-gap: 0.5rem; justify-content: center; margin: 0.2rem 0; }
.kb-row { display: grid; grid-gap: 0.35rem; margin: 0.3rem auto; }
.kb-row-1 { grid-template-columns: repeat(10, 1fr); max-width: 30rem; }
.kb-row-2 { grid-template-columns: repeat(9, 1fr); max-width: 27rem; }
.kb-row-3 { grid-template-columns: 1.5fr repeat(7, 1fr) 1.5fr; max-width: 30rem; }
.kb-btn button { width: 100%; padding: 0.8rem 0.2rem; border-radius: 0.75rem; font-weight: 700; }
.footer { text-align:center; opacity: 0.75; font-size: 0.9rem; margin-top: 1rem; }
.newgame-btn button { width: 100%; padding: 0.75rem; border-radius: 0.9rem; font-weight: 700; }
.rule-box { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 0.8rem; }
</style>"""

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

---------------------- Word List ----------------------

A compact built-in list of common 5-letter words (solution + validity list)

You can expand this list as you like; keep all words lowercase.

WORDS = [ "about","other","which","their","there","first","would","after","where","could", "sound","great","right","think","place","three","small","large","world","house", "party","light","water","table","apple","brick","chair","drive","eager","flame", "grape","happy","index","joker","knock","lemon","mango","night","ocean","paint", "queen","radio","score","tiger","under","vital","whale","xenon","young","zebra", "adore","blush","crisp","dodge","eagle","fable","gloom","honor","irony","jolly", "karma","linen","micro","noble","olive","piano","quiet","rival","sugar","tonic", "ultra","vapor","woven","witty","yield","vivid","stats","delta","omega","gamma", ]

SOLUTIONS = [ "apple","chair","mango","tiger","radio","happy","lemon","zebra","ocean","paint", "quiet","sugar","vapor","woven","delta","vivid","queen","eager","flame","noble", "micro","olive","joker","table","water","grape","adore","blush","crisp","dodge", ]

---------------------- Helpers ----------------------

def new_game(): st.session_state.target = random.choice(SOLUTIONS) st.session_state.guesses: List[str] = [] st.session_state.feedback: List[List[str]] = []  # list of per-letter statuses: absent/present/correct st.session_state.current = "" st.session_state.over = False st.session_state.win = False st.session_state.kb_state = {}  # letter -> strongest seen status

def score_guess(guess: str, target: str) -> List[str]: """Return list of statuses for each letter: 'correct', 'present', 'absent' (Wordle rules).""" statuses = ["absent"] * 5 target_chars = list(target)

# First pass for correct
for i, ch in enumerate(guess):
    if target_chars[i] == ch:
        statuses[i] = "correct"
        target_chars[i] = None  # use up

# Second pass for present
for i, ch in enumerate(guess):
    if statuses[i] == "correct":
        continue
    if ch in target_chars:
        statuses[i] = "present"
        target_chars[target_chars.index(ch)] = None
    else:
        statuses[i] = "absent"
return statuses

def best_status(old: str, new: str) -> str: order = {None: 0, "absent": 1, "present": 2, "correct": 3} return new if order.get(new, 0) >= order.get(old, 0) else old

def submit_guess(): if st.session_state.over: return g = st.session_state.current.lower() if len(g) != 5: st.toast("Enter 5 letters.") return if any(c not in string.ascii_letters for c in g): st.toast("Letters only.") return if g not in WORDS: st.toast("Not in word list.") return

fb = score_guess(g, st.session_state.target)
st.session_state.guesses.append(g)
st.session_state.feedback.append(fb)

# Update keyboard state
for ch, stt in zip(g, fb):
    st.session_state.kb_state[ch] = best_status(st.session_state.kb_state.get(ch), stt)

if g == st.session_state.target:
    st.session_state.over = True
    st.session_state.win = True
elif len(st.session_state.guesses) >= 6:
    st.session_state.over = True
    st.session_state.win = False

st.session_state.current = ""

def keypress(k: str): if st.session_state.over: return if k == "Enter": submit_guess() elif k == "⌫": st.session_state.current = st.session_state.current[:-1] else: if len(st.session_state.current) < 5 and k.isalpha(): st.session_state.current += k.lower()

---------------------- Init State ----------------------

if "target" not in st.session_state: new_game()

---------------------- Header ----------------------

left, mid, right = st.columns([1,2,1]) with mid: st.title("🧩 Wordly") st.caption("A tiny Wordle-style game built with Streamlit — tap to play!")

New Game button

colA, colB, colC = st.columns([1,2,1]) with colB: if st.button("🔄 New Game", use_container_width=True): new_game()

---------------------- Grid Display ----------------------

Build 6 rows. Use feedback for submitted rows; otherwise show current / empty.

rows: List[List[Tuple[str, str]]] = [] for i in range(6): if i < len(st.session_state.guesses): g = st.session_state.guesses[i] fb = st.session_state.feedback[i] rows.append(list(zip(g, fb))) elif i == len(st.session_state.guesses) and not st.session_state.over: # current row (in-progress) cur = st.session_state.current cur_cells = [(cur[j] if j < len(cur) else "", "inprogress") for j in range(5)] rows.append(cur_cells) else: rows.append([(""," "empty") for _ in range(5)])

Render rows

for row in rows: html_cells = [] for ch, stt in row: if stt == "correct": cls = "tile tile-correct" elif stt == "present": cls = "tile tile-present" elif stt == "absent": cls = "tile tile-absent" elif stt == "inprogress": cls = "tile tile-empty" else: cls = "tile tile-empty" content = ch.upper() html_cells.append(f'<div class="{cls}">{content}</div>') st.markdown('<div class="row">' + ''.join(html_cells) + '</div>', unsafe_allow_html=True)

---------------------- On-screen Keyboard ----------------------

Define layout

row1 = list("QWERTYUIOP") row2 = list("ASDFGHJKL") row3 = ["Enter"] + list("ZXCVBNM") + ["⌫"]

Function to style keyboard buttons based on kb_state

KB_COLOR = {"correct": "", "present": "", "absent": ""}  # use Streamlit default colors

def kb_button(label: str, key: str): # Using small unique keys so Streamlit can track presses if st.button(label, key=key, use_container_width=True): keypress(label)

with st.container(): c1 = st.container() with c1: st.markdown("<div class='kb-row kb-row-1'>", unsafe_allow_html=True) for i, k in enumerate(row1): st.markdown("<div class='kb-btn' style='display:inline-block;width:9%;margin:0 0.5%'></div>", unsafe_allow_html=True) st.markdown("</div>", unsafe_allow_html=True)

# Actually render buttons in columns to keep accessibility
# Row 1
cols = st.columns(10, gap="small")
for i, k in enumerate(row1):
    with cols[i]:
        kb_button(k, f"kb1-{k}")

# Row 2
cols = st.columns(9, gap="small")
for i, k in enumerate(row2):
    with cols[i]:
        kb_button(k, f"kb2-{k}")

# Row 3
cols = st.columns(9, gap="small")
for i, k in enumerate(row3):
    with cols[i]:
        kb_button(k, f"kb3-{k}")

Also provide a text field for those who prefer typing

with st.expander("Prefer typing?", expanded=False): t = st.text_input("Type your 5-letter guess and press Enter:", key="typing_input") if t and t.strip() and (len(t.strip()) == 5 or t.strip().lower() == "enter"): st.session_state.current = t.strip().lower()[:5] submit_guess() st.session_state.typing_input = ""

---------------------- Status & Share ----------------------

if st.session_state.over: if st.session_state.win: st.success(f"You got it! ✅ The word was '{st.session_state.target.upper()}'.") else: st.error(f"Out of tries! ❌ The word was '{st.session_state.target.upper()}'.")

# Build share string
squares = {"correct": "🟩", "present": "🟨", "absent": "⬜"}
lines = []
for fb in st.session_state.feedback:
    lines.append(''.join(squares[x] for x in fb))
share = f"Wordly {len(st.session_state.feedback)}/6\n" + "\n".join(lines)

st.text_area("Share your result:", value=share, height=120)

Keyboard legend & rules

with st.container(): st.markdown( """ <div class="rule-box"> <b>How to play:</b> Guess the 5-letter word in at most 6 tries. Tap letters, use <code>⌫</code> to delete and <b>Enter</b> to submit. </div> """, unsafe_allow_html=True, )

st.markdown("<div class='footer'>Built with ❤️ using Streamlit.</div>", unsafe_allow_html=True)

