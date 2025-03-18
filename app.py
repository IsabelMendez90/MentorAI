import os
import streamlit as st

API_KEY = os.getenv("OPENAI_API_KEY")

st.write(f"API Key detectada: {API_KEY[:5]}...")  # Solo muestra los primeros 5 caracteres
