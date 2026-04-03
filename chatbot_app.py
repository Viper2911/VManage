import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def load_rules():
    try:
        with open("hostel_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("hostel_rules.txt not found.")
        st.stop()

RULES_CONTEXT = load_rules()

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

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: Can I keep an empty beer bottle?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_prompt = f"{SYSTEM_PROMPT}\n\nSTUDENT QUESTION: {prompt}"
        try:
            response = st.session_state.chat.send_message(full_prompt)
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")