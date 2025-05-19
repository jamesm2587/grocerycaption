# gemini_services.py
from PIL import Image
import io
import re # For extract_field, if kept here, or pass structured data.

# Moved from main app, this can be a utility within this service or a broader utils file
def extract_field(pattern, text, default=""):
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        val = match.group(1).strip()
        return val if val.lower() != "not found" else default
    return default

def analyze_image_with_gemini(vision_model, image_bytes, prompt_template):
    """
    Analyzes an image using Gemini Vision model.
    Returns the raw analysis text or raises an exception.
    """
    if not vision_model:
        raise ValueError("Vision model is not configured.")
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        response = vision_model.generate_content([prompt_template, pil_image])
        return response.text
    except Exception as e:
        # Log error or handle more gracefully if needed
        raise Exception(f"Gemini image analysis failed: {str(e)}")


def generate_caption_with_gemini(text_model, prompt):
    """
    Generates a caption using Gemini Text model.
    Returns the generated caption or raises an exception.
    """
    if not text_model:
        raise ValueError("Text model is not configured.")
    try:
        response = text_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Log error or handle more gracefully
        raise Exception(f"Gemini caption generation failed: {str(e)}")