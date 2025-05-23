# gemini_services.py
from PIL import Image
import io
import re # For extract_field, if kept here, or pass structured data.

# Moved from main app, this can be a utility within this service or a broader utils file
def extract_field(pattern, text, default=""):
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        val = match.group(1).strip()
        # Handle "Not found" or empty strings more consistently
        if val.lower() in ["not found", "n/a", ""]:
            return default
        return val
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

# Updated Image Analysis Prompt Template
IMAGE_ANALYSIS_PROMPT_TEMPLATE_V3 = (
    "Analyze this grocery sale image. Extract all details precisely. "
    "Respond strictly in this format, ensuring each field is on a new line:\n"
    "Product Name: [Primary product name or names clearly featured for sale]\n"
    "Price: [Price of the primary product, including currency and unit, e.g., $1.99/lb, 2 for $5.00, 99¢ each]\n"
    "Sale Dates: [Sale period, e.g., MM/DD-MM/DD, Ends MM/DD, May 15-20. If year is present, include it.]\n"
    "Store Name: [Visible store name, if any]\n"
    "Promotional Text: [Any other relevant promotional phrases or taglines, like '3 Days Only', 'Special Offer']\n"
    "Product Category: [General category like Produce, Dairy, Meat, Bakery, Pantry, Frozen, Beverages, Snacks, Household. If multiple distinct items, categorize the primary one or provide a comma-separated list if appropriate for a single ad item. Default to 'General Grocery' if unclear.]\n"
    "Detected Brands/Logos: [List any recognizable product brands or logos visible, e.g., Coca-Cola, Lay's. If none, state 'Not found'. Comma-separate if multiple.]\n"
    "Special Attributes: [List any special product attributes visible like Organic, Gluten-Free, Non-GMO, Keto-Friendly, Vegan, Low Sodium, Fair Trade, etc. If none, state 'Not found'. Comma-separate if multiple.]\n"
    "If a field is not found or unclear for any specific line item above, state 'Not found' for that field and only that field."
)
