import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Leer la API Key desde Streamlit Secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

# Crear el modelo de lenguaje con LangChain
llm = ChatOpenAI(
    openai_api_key=API_KEY,
    openai_api_base=API_BASE,
    model_name=MODEL_NAME,
    model_kwargs={
        "headers": {
            "HTTP-Referer": "https://yourwebsite.com",
            "X-Title": "Streamlit GPT",
        }
    },
)

# Plantilla del prompt
template = """Question: {question}
Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=["question"])

# Cadena LLM en LangChain
llm_chain = LLMChain(prompt=prompt, llm=llm)

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
        response = llm_chain.run(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

    except Exception as e:
        st.error(f"Error: {e}")
