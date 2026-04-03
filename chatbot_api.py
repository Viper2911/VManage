import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from pydantic import field_validator
except ImportError:
    from pydantic import validator as field_validator

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="VIT Hostel Rules AI")

def load_rules():
    rules_path = BASE_DIR / "hostel_rules.txt"
    try:
        with rules_path.open("r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"{rules_path.name} not found.")

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
        "Consult the Chief Warden for further clarification."
    )

SYSTEM_PROMPT = f"""You are the VIT Hostel Compliance Bot.
Answer ONLY based on the rules below. Be firm but professional.
If not covered, say 'Consult the Chief Warden for further clarification.'

RULES:
{RULES_CONTEXT}"""

class UserQuery(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be empty.")
        return v.strip()

@app.get("/")
async def root():
    return {"status": "VIT Hostel Rules AI is running"}

@app.post("/api/ai/chat")
async def ask_hostel_ai(query: UserQuery):
    try:
        return {
            "answer": answer_from_rules(query.question),
            "policy_source": "VIT Institute Code of Conduct"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
