import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zhipuai import ZhipuAI

load_dotenv()
GLM_API_KEY = os.getenv("GLM_API_KEY").strip('"').strip("'")

app = FastAPI()

client = ZhipuAI(
    api_key=GLM_API_KEY,
    timeout=httpx.Timeout(timeout=60.0, connect=10.0)
)

def load_rules():
    try:
        with open("hostel_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Rules context file not found."

RULES_CONTEXT = load_rules()

class UserQuery(BaseModel):
    question: str

@app.post("/api/ai/chat")
async def ask_hostel_ai(query: UserQuery):
    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are the VIT Hostel Compliance Bot. Answer based ONLY on these rules: {RULES_CONTEXT}."
                },
                {"role": "user", "content": query.question}
            ],
            stream=False
        )
        return {
            "answer": response.choices[0].message.content,
            "policy_source": "VIT Institute Code of Conduct"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))