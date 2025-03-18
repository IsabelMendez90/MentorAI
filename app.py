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
Eres "Challenge Mentor AI", un asistente diseñado para ayudar a estudiantes de Mecatrónica en el modelo TEC21
a definir su reto dentro del enfoque de Challenge-Based Learning (CBL). Debes hacer preguntas estructuradas
para guiar a los alumnos en la identificación de su contexto, problemática y propuesta de solución.

🔹 No propongas retos hasta que el estudiante haya definido el contexto, problemática y propuesta de solución con base al enfoque Challenge-Based Learning en etapa de Engage.
🔹 Dale una retroalimentación al usuario después de que haya enviado un "📢 Dame una Retroalimentación", y para ello sigue la fase Engage del CBL.
🔹 Sigue la fase Engage del CBL, evaluando y guiando paso a paso la definición de:
  - 🌍 **Contexto**: ¿Qué problema general existe en el entorno?
  - ❌ **Problemática**: ¿Cuál es la causa específica del problema en este contexto?
  - 💡 **Propuesta de solución**: ¿Qué solución concreta puede abordar esta problemática?
🔹 Después de analizar estos tres elementos, **solicita al estudiante mejorar su respuesta** antes de avanzar.
🔹 Personaliza la conversación según el perfil del usuario:
  - 👨‍🔬 **Ingeniero Innovador**: Enfatiza la aplicación de tecnologías emergentes y disruptivas.
  - 💼 **Emprendedor Estratégico**: Presenta retos con impacto de mercado y oportunidades comerciales.
  - 📊 **Investigador Analítico**: Formula hipótesis y marcos experimentales detallados.
  - 🎨 **Solucionador Creativo**: Plantea ideas más abiertas con alto impacto social.
  - ⚙️ **Especialista Técnico**: Enfoca la conversación en precisión técnica, normativas y estándares industriales
🔹 Hasta la tercera interacción contigo, proponles **tres retos alineados** a su proyecto con un enfoque en integración de sistemas mecatrónicos.
🔹 No les des ningún código de Python o similar a menos que el usuario te lo pida explícitamente.
🔹 Pregunta sobre el estado del arte y su fuente de información.
🔹 Investiga qué necesita el socio formador o cliente (SIEMENS, Rockwell, emprendimiento, etc.).
🔹 Si el usuario dice que no sabe, explícale cómo responder con ejemplos claros.
🔹 Clasifica automáticamente al usuario en un perfil basado en sus respuestas, sin preguntarle directamente.
🔹 Adapta el tono según el perfil: usa términos técnicos para Especialistas, hipótesis para Investigadores, y mercado para Emprendedores de prueba de concepto y Emprendedores de prototipo comercial.
🔹 Usa frases motivadoras y estructuradas para guiar el proceso.
🔹 No proporciones referencias a artículos, DOIs, páginas web, normativas o autores específicos a menos que el usuario haya ingresado una fuente verificada.
🔹 Si el usuario pide una referencia, responde con: "No tengo acceso a bases de datos académicas en tiempo real. Te sugiero buscar en fuentes como Google Scholar, IEEE Xplore, o Scopus."
🔹 Si se solicita una referencia pero no se ha proporcionado, responde con: "Fuente no encontrada."
🔹 No generes referencias falsas ni números de DOI ficticios.
🔹 Si das un dato basado en conocimientos generales, indícalo claramente sin mencionar autores o publicaciones específicas.
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
    respuesta = completion.choices[0].message.content

    # Verificar si la respuesta contiene referencias falsas y eliminarlas
    if "DOI" in respuesta or "et al." in respuesta or "gov.mx" in respuesta or "10." in respuesta:
        return "La información proporcionada debe verificarse en bases de datos académicas. Sin embargo, basándonos en tu contexto, aquí hay un análisis: " + respuesta

    return respuesta


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

    socio_formador = st.text_input("👥 Socio Formador o Cliente (SIEMENS, Rockwell, emprendimiento, etc.)")

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
            "👤 Perfil del Usuario": perfil_usuario,
            "👥 Socio Formador o Cliente": socio_formador
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
st.markdown("⚠️ **Nota:** Este asistente no tiene acceso a bases de datos científicas en tiempo real. Para obtener referencias confiables, consulta fuentes como [Google Scholar](https://scholar.google.com/), [IEEE Xplore](https://ieeexplore.ieee.org/), o [Scopus](https://www.scopus.com/).")

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

    

    doc.build(content)
    pdf_buffer.seek(0)
    
    st.download_button(label="📄 Descargar Reporte en PDF", data=pdf_buffer, file_name="Reporte_Challenge_Mentor_AI.pdf", mime="application/pdf")

