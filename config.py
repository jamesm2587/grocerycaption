# config.py
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

def load_and_configure_api():
    """
    Loads API key and configures the Gemini API.
    Prioritizes Streamlit secrets for deployment,
    then .env file for local development,
    and finally direct environment variables.
    """
    api_key = None

    # 1. Try to get the API key from Streamlit secrets (for deployed app)
    try:
        # Check if we are in a Streamlit Cloud environment
        # A more robust check might involve specific environment variables set by Streamlit Cloud
        # For now, st.secrets.get is the primary method.
        if hasattr(st, 'secrets'): # Check if st.secrets exists
            api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception: # Handle cases where st.secrets might not be available or configured
        pass

    # 2. If not found in Streamlit secrets, try .env file (for local development)
    if not api_key:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

    # 3. (Optional) As a final fallback, check direct environment variable
    # This is redundant if load_dotenv worked, but good for other environments
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")


    if not api_key:
        st.error("🔴 GEMINI_API_KEY not found. Please set it in Streamlit secrets (for deployment) or in a .env file / environment variable (for local development).")
        st.info("For local development, create a `.env` file in the project root with `GEMINI_API_KEY='your_key_here'`.")
        st.info("For Streamlit Cloud deployment, add it to your app's secrets in the Streamlit dashboard.")
        st.stop()
        return None, None

    try:
        genai.configure(api_key=api_key)
        vision_model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        text_model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        # You could add a small success message here if running locally and key is found
        # st.sidebar.success("Gemini API configured successfully.") # Example
        return vision_model, text_model
    except Exception as e:
        st.error(f"🔴 Error configuring Gemini API: {e}. Please check your API key and network connection.")
        st.stop()
        return None, None

VISION_MODEL, TEXT_MODEL = load_and_configure_api()
