import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

app = FastAPI(title="VIT Hostel Rules AI")

def load_rules():
    try:
        with open("hostel_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError("hostel_rules.txt not found.")

RULES_CONTEXT = load_rules()

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
        full_prompt = f"{SYSTEM_PROMPT}\n\nSTUDENT QUESTION: {query.question}"
        response = model.generate_content(full_prompt)
        return {
            "answer": response.text,
            "policy_source": "VIT Institute Code of Conduct"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))