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

# MODIFIED: IMAGE_ANALYSIS_PROMPT_TEMPLATE (V4)
IMAGE_ANALYSIS_PROMPT_TEMPLATE = (
    "Analyze this grocery sale image with high precision. Extract details and respond strictly in this format, ensuring each field is on a new line:\n"
    "Product Name: [Identify the primary product name. If multiple names are visible (e.g., English and Spanish), prioritize the name in the largest text. If text sizes are similar, prefer the English name.]\n"
    "Official Brands: [List any recognizable company/product brand names visible, e.g., Coca-Cola, Tyson, Lay's. If none, state 'Not found'.]\n"
    "Product Attributes/Certifications: [List any quality grades, certifications, or descriptive attributes like 'USDA Prime', 'Organic', 'Halal', 'Gluten-Free', 'All Natural'. If none, state 'Not found'.]\n"
    "Full Price String: [Extract the complete, exact price text as it appears, e.g., '$1.99 / lb', '2 for $5.00', '99¢ each'.]\n"
    "Price Notes: [Extract any conditions attached to the price, such as 'Limit 2', 'With Card', 'Digital Coupon Required'. If none, state 'Not found'.]\n"
    "Sale Dates: [Sale period, e.g., MM/DD-MM/DD, Ends MM/DD, May 15-20. Include the year if present.]\n"
    "Store Name: [Visible store name, if any.]\n"
    "Promotional Text: [Any other relevant promotional phrases, like '3 Days Only' or 'Special Offer'.]\n"
    "Product Category: [General category like Produce, Dairy, Meat, Bakery, Pantry, Frozen, Beverages, Snacks, Household. Default to 'General Grocery' if unclear.]\n"
    "If a field is not found or unclear for any specific line item above, state 'Not found' for that field and only that field."
)
