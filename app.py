import streamlit as st
import requests
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configurar la API de OpenRouter
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# ✅ **Instrucciones del Chatbot**
INSTRUCCIONES_SISTEMA = """
Eres Challenge Mentor AI, un asistente diseñado para ayudar a estudiantes de Mecatrónica en el modelo TEC21
a definir su reto dentro del enfoque de Challenge-Based Learning (CBL). Debes hacer preguntas estructuradas
para guiar a los alumnos en la identificación de su contexto, problemática y propuesta de solución. 

🔹 No propongas retos hasta que el estudiante haya definido el contexto, problemática y propuesta de solución.
🔹 Pregunta sobre el estado del arte y su fuente de información.
🔹 Investiga qué necesita su socio formador (SIEMENS, Rockwell, emprendimiento, etc.).
🔹 Clasifica automáticamente al usuario en un perfil basado en sus respuestas, sin preguntarle directamente.
🔹 Adapta el tono según el perfil: usa términos técnicos para Especialistas, hipótesis para Investigadores, y mercado para Emprendedores.
🔹 Usa frases motivadoras y estructuradas para guiar el proceso.

Cuando proporciones datos, SIEMPRE debes incluir referencias reales.
Si no tienes una fuente confiable, responde con "Fuente no encontrada".
No inventes citas en formato APA o referencias falsas.
Si la información proviene de tu entrenamiento, indica que es un dato general y no tiene fuente.
"""

# 🔹 **Función para obtener respuesta del chatbot**
def obtener_respuesta_chat(messages):
    if not API_KEY:
        return "❌ Error: No se encontró la clave API. Configúrala en Streamlit Cloud."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourwebsite.com",  # Cámbialo o elimínalo si no lo necesitas
        "X-Title": "Challenge Mentor AI"
    }

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "system", "content": INSTRUCCIONES_SISTEMA}] + messages
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"❌ Error en la API ({response.status_code}): {response.text}"

    except requests.exceptions.RequestException as e:
        return f"⚠️ Error de conexión: {e}"

# 🔹 **Inicializar estado de la sesión**
if "messages" not in st.session_state:
    st.session_state.messages = []

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "retroalimentacion_completada" not in st.session_state:
    st.session_state.retroalimentacion_completada = False

if "interacciones_chat" not in st.session_state:
    st.session_state.interacciones_chat = 0

# 🔹 **Interfaz en Streamlit**
st.title("🤖 Challenge Mentor AI")
st.subheader("Guía interactiva para definir tu reto en el modelo TEC21 de Mecatrónica.")
st.markdown(
    "Este asistente te ayudará paso a paso a estructurar tu reto dentro del enfoque de **Challenge-Based Learning (CBL)**. "
    "Primero recibirás **retroalimentación** antes de generar un reto definitivo."
)

# 🔹 **Formulario para ingresar datos del proyecto**
with st.form("challenge_form"):
    nombre_proyecto = st.text_input("📌 Nombre del Proyecto", help="Ejemplo: Inspección automática con IA")
    contexto = st.text_area("🌍 Contexto", help="Describe en qué área de Mecatrónica se centra tu proyecto.")
    problema = st.text_area("❌ Problema Principal", help="Explica qué problema intenta resolver tu proyecto.")
    impacto = st.text_area("🎯 Impacto del Problema", help="¿Cómo afecta este problema al público objetivo?")
    propuesta_solucion = st.text_area("💡 Propuesta de Solución", help="¿Qué idea tienes para solucionarlo?")
    
    tipo_proyecto = st.selectbox(
        "⚙️ Tipo de Proyecto",
        ["Desarrollo tecnológico", "Investigación", "Emprendimiento - Prueba de concepto", "Emprendimiento - Prototipo comercial"]
    )

    perfil_usuario = st.selectbox(
        "👤 Perfil del Usuario",
        ["Ingeniero Innovador", "Emprendedor Estratégico", "Investigador Analítico", "Solucionador Creativo", "Especialista Técnico"]
    )

    submit_button = st.form_submit_button("📢 Dame una Retroalimentación")

# 🔹 **Procesar el formulario y obtener retroalimentación**
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

# 🔹 **Mostrar la conversación**
if st.session_state.retroalimentacion_completada:
    st.subheader("📝 Historial de Conversación")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"👨‍🎓 **Tú:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"🤖 **Challenge Mentor AI:** {msg['content']}")

    # 🔹 **Input del Usuario**
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

# 🔹 **Botón de descarga de conversación**
if st.session_state.interacciones_chat >= 3:
    st.subheader("📄 Descargar Reporte de la Conversación")
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle("Reporte de Conversación - Challenge Mentor AI")

    y = 750
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y, "Reporte de Conversación - Challenge Mentor AI")
    y -= 30

    pdf.setFont("Helvetica", 12)
    for msg in st.session_state.messages:
        pdf.drawString(100, y, f"{msg['role'].capitalize()}: {msg['content']}")
        y -= 20
        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()
    pdf_buffer.seek(0)

    st.download_button(label="📄 Descargar Reporte en PDF", data=pdf_buffer, file_name="Reporte_Challenge_Mentor_AI.pdf", mime="application/pdf")
