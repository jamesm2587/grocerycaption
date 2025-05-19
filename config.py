# config.py
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

def load_and_configure_api():
    """Loads API key and configures the Gemini API."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # For deployed Streamlit apps, use st.secrets
    # api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

    if not api_key:
        st.error("🔴 GEMINI_API_KEY not found. Please set it in your .env file (for local) or Streamlit secrets (for deployment).")
        st.stop()
        return None, None

    try:
        genai.configure(api_key=api_key)
        vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        text_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        return vision_model, text_model
    except Exception as e:
        st.error(f"🔴 Error configuring Gemini API: {e}. Please check your API key and network connection.")
        st.stop()
        return None, None

VISION_MODEL, TEXT_MODEL = load_and_configure_api()