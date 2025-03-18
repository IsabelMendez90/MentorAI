import streamlit as st
from langchain_openai import ChatOpenAI  # ✅ Cambió de módulo
from langchain_core.prompts import PromptTemplate  # ✅ Nuevo módulo
from langchain_core.runnables import RunnableLambda  # ✅ Nuevo método

# Leer la API Key desde Streamlit Secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

# Verificar si la API Key se carga correctamente
if not API_KEY or API_KEY == "sk-or********":
    st.error("❌ ERROR: No se encontró una API Key válida en Streamlit Secrets.")
    st.stop()

st.write(f"🔑 API Key detectada: {API_KEY[:5]}********")

# ✅ Crear el modelo de lenguaje con el nuevo módulo de LangChain
llm = ChatOpenAI(
    api_key=API_KEY,
    base_url=API_BASE,
    model=MODEL_NAME
)

# ✅ Nueva forma de definir el prompt en LangChain 1.0
prompt = PromptTemplate.from_template("Question: {question}\nAnswer:")

# ✅ Nueva forma de ejecutar el modelo
chain = prompt | llm | RunnableLambda(lambda x: x["content"])

# ---------------- STREAMLIT UI ----------------
st.title("💬 Chat con LangChain y OpenRouter")

# Inicializar historial de mensajes en sesión
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! How can I help you?"}
    ]

# Formulario para ingresar la pregunta
with st.form("chat_input", clear_on_submit=True):
    a, b = st.columns([4, 1])
    user_input = a.text_input("Your message:", placeholder="Ask me something...")
    b.form_submit_button("Send", use_container_width=True)

# Mostrar mensajes previos en la interfaz
for i, msg in enumerate(st.session_state.messages):
    st.chat_message(msg["role"]).write(msg["content"])

if user_input:
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Obtener respuesta del modelo
    try:
        response = chain.invoke({"question": user_input})  # ✅ Cambió `.run()` por `.invoke()`
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

    except Exception as e:
        st.error(f"Error: {e}")
