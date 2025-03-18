import openai
import streamlit as st
from streamlit_chat import message
import json

# Configuración de API directamente
API_KEY = "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"  # Sustituye con tu API key
API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

st.title("💬 Streamlit GPT")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

with st.form("chat_input", clear_on_submit=True):
    a, b = st.columns([4, 1])
    user_input = a.text_input(
        label="Your message:",
        placeholder="What would you like to say?",
        label_visibility="collapsed",
    )
    b.form_submit_button("Send", use_container_width=True)

for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["role"] == "user", key=i)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True)
    
    openai.api_key = API_KEY
    openai.api_base = API_BASE

    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=st.session_state.messages,
            headers={
                "HTTP-Referer": "https://yourwebsite.com",  # Opcional
                "X-Title": "Streamlit GPT",  # Opcional
            },
        )

        if isinstance(response, str):  # Manejo de respuesta en formato str
            response = json.loads(response)

        msg = response["choices"][0]["message"]
        st.session_state.messages.append(msg)
        message(msg["content"])

    except Exception as e:
        st.error(f"Error: {e}")
