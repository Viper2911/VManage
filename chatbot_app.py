import os
import re
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def load_rules():
    rules_path = BASE_DIR / "hostel_rules.txt"
    try:
        with rules_path.open("r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"{rules_path.name} not found.")
        st.stop()

RULES_CONTEXT = load_rules()
RULE_LINES = [line.strip() for line in RULES_CONTEXT.splitlines() if line.strip()]

STOPWORDS = {
    "about", "allowed", "am", "an", "and", "are", "can", "do", "for", "how",
    "hostel", "i", "in", "inside", "is", "it", "keep", "me", "my", "of", "on",
    "or", "the", "to", "what", "with"
}

SYNONYMS = {
    "alcohol": {"alcohol", "liquor", "beer", "bottle", "drinking", "drink"},
    "smoking": {"smoking", "smoke", "cigarette", "cigarettes", "vape", "vaping", "e-smoking"},
    "ragging": {"ragging", "bully", "bullying", "harass", "harassment"},
    "drugs": {"drugs", "drug", "substance", "abuse", "narcotics"},
    "theft": {"theft", "steal", "stealing", "stolen"},
    "property": {"property", "damage", "damaging", "break", "broken"},
    "uniform": {"uniform", "dress", "dressing", "attire", "clothes"},
    "gambling": {"gambling", "gamble", "forgery", "marketing"},
    "cyber": {"cyber", "crime", "crimes", "defame", "defaming", "reputation"},
    "fighting": {"fighting", "fight", "quarrel", "quarreling", "slander", "injury"},
    "expulsion": {"expulsion", "expelled", "debarred", "admission", "cancelled"},
    "consequences": {"consequences", "privileges", "scholarships", "placement", "penalty", "punishment"},
}

def normalize_tokens(text: str) -> set[str]:
    raw_tokens = set(re.findall(r"\b[a-zA-Z][a-zA-Z-]{1,}\b", text.lower()))
    tokens = {token for token in raw_tokens if token not in STOPWORDS}
    expanded_tokens = set(tokens)

    for token in tokens:
        for canonical, variants in SYNONYMS.items():
            if token in variants:
                expanded_tokens.add(canonical)

    return expanded_tokens

def answer_from_rules(question: str) -> str:
    tokens = normalize_tokens(question)
    scored_lines = []

    for line in RULE_LINES:
        line_tokens = normalize_tokens(line)
        overlap = tokens & line_tokens
        if overlap:
            score = len(overlap)
            lower_line = line.lower()
            if any(marker in lower_line for marker in ("strictly prohibited", "zero tolerance", "violation")):
                score += 1
            scored_lines.append((score, len(overlap), line))

    scored_lines.sort(key=lambda item: (item[0], item[1]), reverse=True)
    matched_lines = []
    seen_lines = set()
    best_score = scored_lines[0][0] if scored_lines else 0
    min_score = max(2, best_score - 1)

    for score, _, line in scored_lines:
        if score < min_score:
            continue
        if line not in seen_lines:
            matched_lines.append(line)
            seen_lines.add(line)
        if len(matched_lines) == 2:
            break

    if matched_lines:
        intro = "Based on the hostel rules:\n\n"
        return intro + "\n".join(matched_lines)

    return (
        "Your question is not clearly covered by the hostel rules. "
        "Contact the Chief Warden for clarification."
    )

SYSTEM_PROMPT = f"""You are the VIT Hostel Compliance AI.
Answer ONLY based on the rules below. Be firm but professional.
If not covered, say 'Contact the Chief Warden for clarification.'

RULES:
{RULES_CONTEXT}"""

st.set_page_config(page_title="VIT Rules AI Assistant", layout="centered")
st.title("🤖 VIT Hostel Rules AI")
st.caption("Ask anything about the Code of Conduct, Ragging policies, or Misconduct rules.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Can I keep an empty beer bottle?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            answer = answer_from_rules(prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")
