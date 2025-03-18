import openai
import streamlit as st
from streamlit_chat import message
import json

# Configuración de API directamente
API_KEY = "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"  # Sustituye con tu API key
API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

# Configurar el cliente de OpenAI con la API Key
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

st.title("💬 Streamlit GPT")

# Inicializar historial de mensajes si no existe
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Formulario de entrada del usuario
with st.form("chat_input", clear_on_submit=True):
    a, b = st.columns([4, 1])
    user_input = a.text_input(
        label="Your message:",
        placeholder="What would you like to say?",
        label_visibility="collapsed",
    )
    b.form_submit_button("Send", use_container_width=True)

# Mostrar historial de mensajes
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["role"] == "user", key=i)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.messages
        )

        if response.choices:
            msg = response.choices[0].message
            st.session_state.messages.append({"role": msg.role, "content": msg.content})
            message(msg.content, is_user=False)

    except openai.AuthenticationError:
        st.error("Error de autenticación. Verifica tu API key en OpenRouter.")
    except Exception as e:
        st.error(f"Error: {e}")
