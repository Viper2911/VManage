import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI("ChatBot")

genai.configure(api_key="")
model=genai.GenerativeModel('gemini-1.5-flash')

with open("hostel_rules.txt",'r') as f:
    rules_context=f.read()

class UserQuery(BaseModel):
    question: str

@app.post(/api/ai/chat)
async def ask_hostel_ai(query: UserQuery):
    system_prompt = f"""
    You are the 'VIT Hostel Compliance Bot'. Your job is to strictly enforce the following code of conduct.
    Answer student questions based ONLY on these rules. 
    If a student asks about something prohibited (like smoking or alcohol), remind them of the specific point in the rules.
    If they ask about something not mentioned, tell them to 'Consult the Chief Warden for further clarification.'
    
    Rules Context: {rules_context}
    Student Question: {query.question}
    """
    response=model.generate_content(system_prompt)

    return{
        "answer": response.text,
        "policy_source": "VIT Institute Code of Conduct"
    }