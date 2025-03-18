import streamlit as st
import openai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

#  **Rol Correcto del Chatbot (Solo para uso interno)** 
INSTRUCCIONES_SISTEMA = """
Eres Challenge Mentor AI, un asistente diseñado para ayudar a estudiantes de Mecatrónica en el modelo TEC21
a definir su reto dentro del enfoque de Challenge-Based Learning (CBL). Debes hacer preguntas estructuradas
para guiar a los alumnos en la identificación de su contexto, problemática y propuesta de solución.

🔹 No propongas retos hasta que el estudiante haya definido el contexto, problemática y propuesta de solución.
🔹 No les des ningún código a menos que el usuario te lo pida explícitametne.
🔹 Pregunta sobre el estado del arte y su fuente de información.
🔹 Investiga qué necesita su socio formador (SIEMENS, Rockwell, emprendimiento, etc.).
🔹 Si el usuario dice que no sabe, explícale cómo responder con ejemplos claros.
🔹 Clasifica automáticamente al usuario en un perfil basado en sus respuestas, sin preguntarle directamente.
🔹 Adapta el tono según el perfil: usa términos técnicos para Especialistas, hipótesis para Investigadores, y mercado para Emprendedores de prueba de concepto y Emprendedores de prototipo comercial.
🔹 Usa frases motivadoras y estructuradas para guiar el proceso.

Cuando proporciones datos, SIEMPRE debes incluir referencias reales.
Si no tienes una fuente confiable, responde con "Fuente no encontrada".
No inventes citas en formato APA o referencias falsas.
Si la información proviene de tu entrenamiento, indica que es un dato general y no tiene fuente.
"""

# Leer la API Key desde Streamlit Secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-r1:free"

# **🔹 Función para obtener respuesta del chatbot**
def obtener_respuesta_chat(messages):
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=API_BASE
    )
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": INSTRUCCIONES_SISTEMA}] + messages
    )
    return completion.choices[0].message.content

# **🔹 Inicializar historial de mensajes y estado si no existen**
if "messages" not in st.session_state:
    st.session_state.messages = []

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "retroalimentacion_completada" not in st.session_state:
    st.session_state.retroalimentacion_completada = False

if "interacciones_chat" not in st.session_state:
    st.session_state.interacciones_chat = 0

# **🔹 Título e introducción**
st.title("🤖 Challenge Mentor AI")
st.subheader("Guía interactiva para definir tu reto en el modelo TEC21 de Mecatrónica.")
st.markdown(
    "Este asistente te ayudará paso a paso a estructurar tu reto dentro del enfoque de **Challenge-Based Learning (CBL)**. "
    "Primero recibirás **retroalimentación** antes de generar un reto definitivo.")

# ✅ **Formulario para capturar información del usuario**
with st.form("challenge_form"):
    nombre_proyecto = st.text_input("📌 Nombre del Proyecto")
    contexto = st.text_area("🌍 Contexto")
    problema = st.text_area("❌ Problema Principal")
    impacto = st.text_area("🎯 Impacto del Problema")
    propuesta_solucion = st.text_area("💡 Propuesta de Solución")

    tipo_proyecto = st.selectbox(
        "⚙️ Tipo de Proyecto",
        ["Desarrollo tecnológico", "Investigación", "Emprendimiento - Prueba de concepto", "Emprendimiento - Prototipo comercial"]
    )

    perfil_usuario = st.selectbox(
        "👤 Perfil del Usuario",
        ["Ingeniero Innovador", "Emprendedor Estratégico", "Investigador Analítico", "Solucionador Creativo", "Especialista Técnico"]
    )

    submit_button = st.form_submit_button("📢 Dame una Retroalimentación")

# ✅ **Procesar información del formulario**
if submit_button:
    if not nombre_proyecto or not contexto or not problema or not propuesta_solucion:
        st.warning("⚠️ Completa todos los campos antes de continuar.")
    else:
        st.session_state.responses = {
            "📌 Nombre del Proyecto": nombre_proyecto,
            "🌍 Contexto": contexto,
            "❌ Problema Principal": problema,
            "🎯 Impacto": impacto,
            "💡 Propuesta de Solución": propuesta_solucion,
            "⚙️ Tipo de Proyecto": tipo_proyecto,
            "👤 Perfil del Usuario": perfil_usuario
        }

        user_message = "\n".join([f"**{key}:** {value}" for key, value in st.session_state.responses.items()])
        st.session_state.messages.append({"role": "user", "content": user_message})

        with st.spinner("📢 Generando retroalimentación..."):
            respuesta_chatbot = obtener_respuesta_chat(st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": respuesta_chatbot})
        st.session_state.retroalimentacion_completada = True
        st.rerun()

# ✅ **Mostrar historial de conversación**
if st.session_state.retroalimentacion_completada:
    st.subheader("📝 Historial de Conversación")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"👨‍🎓 **Tú:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"🤖 **Challenge Mentor AI:** {msg['content']}")

    user_input = st.text_area("💬 Escribe aquí tu pregunta:", height=100)

    if st.button("Enviar"):
        if user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("🤖 Generando respuesta..."):
                chatbot_response = obtener_respuesta_chat(st.session_state.messages)

            st.session_state.messages.append({"role": "assistant", "content": chatbot_response})

            st.session_state.interacciones_chat += 1
            st.rerun()
        else:
            st.warning("⚠️ Por favor, escribe tu pregunta antes de enviar.")

# ✅ **Descargar Reporte en PDF**
if st.session_state.interacciones_chat >= 3:
    st.subheader("📄 Descargar Reporte de la Conversación")
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Reporte de Conversación - Challenge Mentor AI", styles["Title"]))
    content.append(Spacer(1, 12))

    for msg in st.session_state.messages:
        role = "👨‍🎓 Usuario:" if msg["role"] == "user" else "🤖 Challenge Mentor AI:" 
        content.append(Paragraph(f"<b>{role}</b> {msg['content']}", styles["Normal"]))
        content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Los retos sugeridos podrían ser:</b>", styles["Heading2"]))

    doc.build(content)
    pdf_buffer.seek(0)
    
    st.download_button(label="📄 Descargar Reporte en PDF", data=pdf_buffer, file_name="Reporte_Challenge_Mentor_AI.pdf", mime="application/pdf")

