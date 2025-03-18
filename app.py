import openai
import streamlit as st
from streamlit_chat import message
import json

# Configuración de API directamente
API_KEY = "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"  # Sustituye con tu API key
API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

# Inicializar cliente OpenAI con autenticación correcta
client = openai.OpenAI(
    base_url=API_BASE,
    api_key=API_KEY
)

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

# Mostrar mensajes previos
for i, msg in enumerate(st.session_state.messages):
    if isinstance(msg, dict) and "content" in msg and "role" in msg:
        message(msg["content"], is_user=msg["role"] == "user", key=f"msg_{i}")
    else:
        st.warning(f"Formato de mensaje incorrecto en índice {i}: {msg}")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True, key=f"user_{len(st.session_state.messages)}")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.messages,
            extra_headers={
                "Authorization": f"Bearer {API_KEY}",  # ✅ Incluir la API key aquí
                "HTTP-Referer": "https://yourwebsite.com",  # Opcional
                "X-Title": "Streamlit GPT",  # Opcional
            }
        )

        # Verificar que la respuesta tenga el formato esperado
        if response and hasattr(response, "choices") and len(response.choices) > 0:
            msg = response.choices[0].message
            if hasattr(msg, "content") and hasattr(msg, "role"):
                st.session_state.messages.append({"role": msg.role, "content": msg.content})
                message(msg.content, is_user=False, key=f"assistant_{len(st.session_state.messages)}")
            else:
                st.error("Formato de respuesta inesperado.")
        else:
            st.error("La respuesta de la API está vacía o mal formada.")

    except openai.APIConnectionError:
        st.error("Error de conexión con OpenAI. Verifica tu conexión a internet.")
    except openai.AuthenticationError:
        st.error("Error de autenticación. Verifica que tu API key sea válida.")
    except Exception as e:
        st.error(f"Error: {e}")
