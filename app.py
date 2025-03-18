import requests
import json
import os

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def obtener_respuesta_chat(messages):
    if not API_KEY:
        return "❌ Error: No se encontró la clave API. Configúrala en Streamlit Cloud."

    headers = {
        "Authorization": f"Bearer {API_KEY.strip()}",  # Elimina espacios en blanco extra
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "system", "content": INSTRUCCIONES_SISTEMA}] + messages
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "❌ Error 401: La clave API no es válida o no está activa en OpenRouter."
        else:
            return f"❌ Error en la API ({response.status_code}): {response.text}"

    except requests.exceptions.RequestException as e:
        return f"⚠️ Error de conexión: {e}"
