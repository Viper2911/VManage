import os
import httpx
import streamlit as st
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
GLM_API_KEY = os.getenv("GLM_API_KEY").strip('"').strip("'")

st.set_page_config(page_title="VIT Rules AI Assistant", layout="centered")

client = ZhipuAI(
    api_key=GLM_API_KEY,
    timeout=httpx.Timeout(timeout=120.0, connect=30.0) 
)

def load_rules():
    try:
        with open("hostel_rules.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Rules file not found."

RULES_CONTEXT = load_rules()

st.title("🤖 VIT Hostel Rules AI (GLM)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tell me about hostel rules"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            response = client.chat.completions.create(
                model="glm-4", 
                messages=[
                    {"role": "system", "content": f"You are the VIT Hostel Compliance AI. Answer ONLY based on these rules: {RULES_CONTEXT}"},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {e}")