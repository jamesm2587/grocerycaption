# app.py
import streamlit as st
import datetime
import io
import re
from streamlit.components.v1 import html as st_html_component
import html as html_escaper
import copy
import json
import os
import tempfile
import cv2
# Ensure numpy is imported if you use it directly, though cv2 uses it internally
# import numpy as np

# Local imports
from config import VISION_MODEL, TEXT_MODEL
from constants import INITIAL_BASE_CAPTIONS, TONE_OPTIONS, PREDEFINED_PRICES
from utils import (
    get_current_day_for_teds, get_holiday_context, format_dates_for_caption_context,
    get_final_price_string, find_store_key_by_name, try_parse_date_from_image_text
)
from gemini_services import analyze_image_with_gemini, generate_caption_with_gemini, extract_field, IMAGE_ANALYSIS_PROMPT_TEMPLATE

CUSTOM_STORES_FILE = "custom_stores.json"

# --- NEW UI Function ---
def load_custom_ui():
    """Injects custom CSS for a more appealing UI."""
    st.markdown("""
        <style>
            /* --- GENERAL --- */
            .stApp {
                /* Theme is set in .streamlit/config.toml */
            }
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            h1, h2, h3, h4, h5, h6 {
                font-weight: 600; /* Bolder headers */
            }

            /* --- TITLE --- */
            h1 { /* Main title style */
                text-align: center;
                font-size: 2.5rem; /* Adjusted for better visual hierarchy */
                letter-spacing: -1px;
                padding-bottom: 1rem;
                border-bottom: 1px solid #2a2d34; /* Use a subtle border from your theme */
                margin-bottom: 2rem; /* More space after title */
            }

            /* --- BUTTONS --- */
            .stButton > button {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                transition: all 0.2s ease-in-out;
                border-width: 1px; /* Ensure border is visible for secondary */
            }
            /* Primary Button (e.g., Analyze) */
            div[data-testid="stButton"] > button[kind="primary"] {
                 background-color: #6c5ce7; /* primaryColor from theme */
                 color: white;
                 border: none; /* Primary buttons might not need a border if background is strong */
            }
            div[data-testid="stButton"] > button[kind="primary"]:hover {
                 background-color: #5848c7; /* Darker shade for hover */
            }
             /* Secondary Button (e.g., Remove, Generate for item) */
            div[data-testid="stButton"] > button[kind="secondary"] {
                border-color: #4A4D56; /* A slightly lighter border than darkest background */
            }
            div[data-testid="stButton"] > button[kind="secondary"]:hover {
                border-color: #6c5ce7; /* primaryColor on hover */
                color: #6c5ce7; /* primaryColor text on hover */
            }

            /* --- FILE UPLOADER --- */
            div[data-testid="stFileUploader"] {
                border: 2px dashed #4A4D56; /* Dashed border */
                background-color: #1a1c22; /* Darker than secondaryBg for contrast */
                border-radius: 12px;
                padding: 1.5rem;
            }
            div[data-testid="stFileUploader"] label { /* Uploader label */
                font-size: 1.1rem;
                font-weight: 600;
            }

            /* --- SIDEBAR --- */
            div[data-testid="stSidebar"] > div:first-child {
                background-color: #1a1c22; /* Darker shade for sidebar */
                border-right: 1px solid #2a2d34; /* Subtle separator */
            }

            /* --- Expander in Sidebar --- */
            div[data-testid="stSidebar"] div[data-testid="stExpander"] { /* Target expander in sidebar specifically */
                 border: 1px solid #2a2d34;
                 border-radius: 8px;
                 background-color: #262730; /* secondaryBackgroundColor */
                 margin-bottom: 1rem; /* Add some space below sidebar expanders */
            }
            div[data-testid="stSidebar"] div[data-testid="stExpander"] summary { /* Expander header */
                font-weight: 600;
                color: #FAFAFA; /* textColor */
            }

            /* --- Expander in Main Content (File Previews) --- */
            .main div[data-testid="stExpander"] {
                 border: 1px solid #2a2d34;
                 border-radius: 8px;
                 background-color: #1a1c22; /* Slightly darker for main content expanders */
                 margin-bottom: 1.5rem;
            }
            .main div[data-testid="stExpander"] summary {
                font-weight: 600;
                color: #FAFAFA;
                padding: 0.5rem 0rem; /* Add some padding to summary */
            }
            .main div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
                padding-top: 1rem; /* Space between summary and content */
            }


            /* --- BORDERED CONTAINERS / CARDS for individual items --- */
             div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div {
                background-color: #1a1c22;
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                border: 1px solid #2a2d34;
                padding: 1.5rem; /* Added more padding inside the card */
                margin-bottom: 1.5rem; /* Space between cards */
            }

            /* --- Form Elements Spacing within Cards --- */
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div .stTextInput,
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div .stTextArea,
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div .stSelectbox,
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div .stDateInput,
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div .stCheckbox {
                margin-bottom: 1rem; /* Consistent bottom margin for form elements */
            }

            /* --- Labels for Form Elements --- */
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div label {
                margin-bottom: 0.3rem; /* Space between label and input */
                display: inline-block; /* Allows margin-bottom to work as expected */
                font-weight: 500; /* Slightly less bold than headers */
            }

            /* --- Text Input & Text Area --- */
            .stTextInput input, .stTextArea textarea {
                border-radius: 8px !important;
                border: 1px solid #4A4D56 !important;
                background-color: #262730 !important;
                color: #FAFAFA !important;
                padding: 0.5rem 0.75rem !important; /* Adjust padding for input fields */
            }
            .stTextInput input:focus, .stTextArea textarea:focus {
                border-color: #6c5ce7 !important;
                box-shadow: 0 0 0 0.2rem rgba(108, 92, 231, 0.25) !important;
            }

            /* --- Selectbox --- */
            .stSelectbox > div[data-baseweb="select"] > div {
                border-radius: 8px !important;
                border: 1px solid #4A4D56 !important;
                background-color: #262730 !important;
                padding-top: 2px !important; /* Fine-tune selectbox padding */
                padding-bottom: 2px !important;
            }
             .stSelectbox > div[data-baseweb="select"] > div:focus-within {
                 border-color: #6c5ce7 !important;
                 box-shadow: 0 0 0 0.2rem rgba(108, 92, 231, 0.25) !important;
             }

            /* --- Date Input --- */
            .stDateInput input {
                 border-radius: 8px !important;
                 border: 1px solid #4A4D56 !important;
                 background-color: #262730 !important;
                 padding: 0.5rem 0.75rem !important; /* Adjust padding */
            }
            .stDateInput input:focus {
                 border-color: #6c5ce7 !important;
                 box-shadow: 0 0 0 0.2rem rgba(108, 92, 231, 0.25) !important;
            }

            /* --- Checkbox --- */
            .stCheckbox label {
                font-size: 1rem;
                padding-top: 0.25rem; /* Align checkbox label better */
            }

            /* Style for st.video to make it fit container width */
            .stVideo {
                width: 100%;
                margin-bottom: 0.5rem; /* Space below video in preview grid */
            }
            .stVideo video {
                width: 100%;
                border-radius: 8px;
            }

            /* Specific Spacing for Two-Column Date Inputs */
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div [data-testid="stHorizontalBlock"] .stDateInput {
                 margin-bottom: 0; /* Remove bottom margin if they are side-by-side */
            }
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] > div [data-testid="stHorizontalBlock"] {
                 margin-bottom: 1rem; /* Ensure the row of date pickers has overall margin */
            }


        </style>
    """, unsafe_allow_html=True)


# --- Video Helper Functions ---
def get_video_thumbnail(video_bytes):
    """Extracts the first frame of a video and returns it as JPG bytes."""
    try:
        # OpenCV needs a file path to read from, so we use a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(video_bytes)
            video_filename = temp_video_file.name

        cap = cv2.VideoCapture(video_filename)
        success, frame = cap.read()
        cap.release()
        os.unlink(video_filename)  # Clean up the temporary file

        if success:
            is_success, buffer = cv2.imencode(".jpg", frame)
            if is_success:
                return buffer.tobytes()
    except Exception as e:
        st.warning(f"Could not generate video thumbnail: {e}")
    return None # Return None if thumbnail generation fails

def analyze_video_frames(vision_model, video_bytes, prompt):
    """
    Analyzes frames from a video using Gemini, scores each analysis,
    and returns the analysis text from the frame with the best score.
    """
    # Use a temporary file for OpenCV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_bytes)
        video_filename = temp_video_file.name

    cap = cv2.VideoCapture(video_filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30  # Assume a default FPS if it's not available

    # Sample one frame per second
    frame_interval = int(fps)

    best_analysis_text = ""
    max_score = -1
    # analyzed_frames = 0 # Not used currently

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame if it's at the desired interval
        if frame_count % frame_interval == 0:
            is_success, buffer = cv2.imencode(".jpg", frame)
            if is_success:
                frame_bytes = buffer.tobytes()
                try:
                    analysis_text = analyze_image_with_gemini(vision_model, frame_bytes, prompt)
                    # analyzed_frames += 1

                    # Score the analysis based on how many key fields are filled
                    score = 0
                    if extract_field(r"^Product Name: (.*)$", analysis_text, default="Not found") != "Not found": score += 2 # Prioritize product name
                    if extract_field(r"^Price: (.*)$", analysis_text, default="Not found") != "Not found": score += 2 # and price
                    if extract_field(r"^Sale Dates: (.*)$", analysis_text, default="Not found") != "Not found": score += 1
                    if extract_field(r"^Store Name: (.*)$", analysis_text, default="Not found") != "Not found": score += 1

                    if score > max_score:
                        max_score = score
                        best_analysis_text = analysis_text
                        # Early exit if we get a "perfect" score (all fields found)
                        if max_score >= 6: # Max possible score with current weighting
                            break
                except Exception as e:
                    # Silently ignore frames that fail analysis to not interrupt the batch
                    print(f"Frame analysis failed: {e}")

        frame_count += 1

    cap.release()
    os.unlink(video_filename)

    if not best_analysis_text:
        # Provide a more generic error if no frame yielded good results
        raise Exception("Video analysis failed. No valid information could be extracted from the video frames.")

    return best_analysis_text

# --- Callback function for removing an uploaded file ---
def remove_file_at_index(index_to_remove):
    if 'uploaded_files_info' in st.session_state and \
       0 <= index_to_remove < len(st.session_state.uploaded_files_info):

        removed_file_name = st.session_state.uploaded_files_info[index_to_remove]['name']
        st.session_state.uploaded_files_info.pop(index_to_remove)

        if not st.session_state.uploaded_files_info:
            st.session_state.analyzed_image_data_set = []
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
            st.session_state.last_caption_by_store = {}
            st.session_state.info_message_after_action = "All files and associated data have been cleared."
            st.session_state.uploader_key_suffix = st.session_state.get('uploader_key_suffix', 0) + 1
        elif 'analyzed_image_data_set' in st.session_state and st.session_state.analyzed_image_data_set:
            # If there were previous analyses, clear them as they are now out of sync
            st.session_state.analyzed_image_data_set = []
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
            st.session_state.last_caption_by_store = {} # Also clear continuity
            st.session_state.info_message_after_action = f"File '{removed_file_name}' removed. Previous analysis and continuity references cleared. Please re-analyze remaining files."
        else:
            st.session_state.info_message_after_action = f"File '{removed_file_name}' removed."


# --- Callback function for removing all uploaded files and data ---
def handle_remove_all_images():
    st.session_state.uploaded_files_info = []
    st.session_state.analyzed_image_data_set = []
    st.session_state.last_caption_by_store = {}
    if 'analyzed_image_data_set_source_length' in st.session_state:
        del st.session_state.analyzed_image_data_set_source_length
    st.session_state.is_analyzing_images = False
    st.session_state.is_batch_generating_captions = False
    st.session_state.error_message = "" # Clear any previous errors
    st.session_state.info_message_after_action = "All uploaded files and their associated data have been cleared."
    st.session_state.uploader_key_suffix = st.session_state.get('uploader_key_suffix', 0) + 1 # Reset uploader


# --- Streamlit App State Initialization ---
def initialize_session_state():
    # Initialize custom_base_captions first as other defaults might depend on it indirectly
    if 'custom_base_captions' not in st.session_state:
        loaded_custom_captions = {}
        try:
            with open(CUSTOM_STORES_FILE, 'r') as f:
                loaded_custom_captions = json.load(f)
            if not isinstance(loaded_custom_captions, dict):
                st.warning(f"{CUSTOM_STORES_FILE} does not contain a valid dictionary. Starting with no custom stores.")
                loaded_custom_captions = {}
        except FileNotFoundError:
            # This is normal if the file hasn't been created yet
            pass
        except json.JSONDecodeError:
            st.error(f"Error decoding {CUSTOM_STORES_FILE}. File might be corrupted. Starting with no custom stores for this session.")
            loaded_custom_captions = {}
        st.session_state.custom_base_captions = loaded_custom_captions

    default_store_key = None
    combined_captions_for_default = get_combined_captions() # Call after custom_base_captions is set
    if combined_captions_for_default:
        default_store_key = list(combined_captions_for_default.keys())[0]

    defaults = {
        'analyzed_image_data_set': [],
        'global_selected_store_key': default_store_key,
        'global_selected_tone': TONE_OPTIONS[0]['value'] if TONE_OPTIONS else None,
        'uploaded_files_info': [],
        'error_message': "",
        'is_analyzing_images': False,
        'is_batch_generating_captions': False,
        'info_message_after_action': "",
        'last_caption_by_store': {},
        'uploader_key_suffix': 0,
        # 'custom_base_captions' is already initialized above
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Function to get combined captions (initial + custom) ---
def get_combined_captions():
    combined = copy.deepcopy(INITIAL_BASE_CAPTIONS)
    custom_captions = st.session_state.get('custom_base_captions', {}) # Ensure this is accessed after init
    if isinstance(custom_captions, dict):
        for store_key, store_sale_types in custom_captions.items():
            if store_key not in combined:
                combined[store_key] = {}
            if isinstance(store_sale_types, dict): # Ensure sale types is a dict
                 combined[store_key].update(store_sale_types)
    return combined

# --- Main App UI ---
def main():
    st.set_page_config(layout="wide", page_title="Caption Generator")
    load_custom_ui()  # Load the new UI styles at the very beginning

    st.title(" Social Media Caption Generator ")

    initialize_session_state() # Initialize session state variables
    current_combined_captions = get_combined_captions() # Get current combined captions data

    # Check for API model availability
    if not VISION_MODEL or not TEXT_MODEL:
        st.error("🔴 Gemini Models not available. Please check configuration.")
        st.stop()

    # Display any error or info messages from previous actions
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = "" # Clear after displaying

    if st.session_state.info_message_after_action:
        st.info(st.session_state.info_message_after_action)
        st.session_state.info_message_after_action = "" # Clear after displaying

    # --- Sidebar ---
    with st.sidebar:
        st.header("Global Settings")

        # Tone Selector
        tone_labels_dict = {tone['value']: tone['label'] for tone in TONE_OPTIONS}
        current_global_tone = st.session_state.get('global_selected_tone', TONE_OPTIONS[0]['value'] if TONE_OPTIONS else None)

        if not TONE_OPTIONS: # Should not happen with constants.py, but good check
            st.sidebar.warning("No tone options defined.")
        elif current_global_tone not in tone_labels_dict: # If saved state is invalid
            current_global_tone = TONE_OPTIONS[0]['value'] if TONE_OPTIONS else None
            st.session_state.global_selected_tone = current_global_tone # Reset to default

        if TONE_OPTIONS and current_global_tone is not None:
            try:
                tone_index = list(tone_labels_dict.keys()).index(current_global_tone)
                selected_tone_val = st.selectbox(
                    "Caption Tone", options=list(tone_labels_dict.keys()),
                    format_func=lambda x: tone_labels_dict[x],
                    index=tone_index,
                    key="global_tone_selector" # Keep key for state
                )
                if selected_tone_val and selected_tone_val != st.session_state.global_selected_tone:
                     st.session_state.global_selected_tone = selected_tone_val
            except ValueError: # Should not happen if current_global_tone is validated
                st.sidebar.warning("Could not load saved tone, defaulting.")
                st.session_state.global_selected_tone = TONE_OPTIONS[0]['value'] if TONE_OPTIONS else None


        # Add New Store Definition Form
        with st.expander("➕ Add New Store Definition (Permanent)"): # Permanent implies saving to file
            with st.form("new_store_form", clear_on_submit=True):
                st.caption("Define a new store and one sale type. Data is saved to custom_stores.json.")

                store_name_form = st.text_input("Store Name*", help="e.g., 'My Corner Shop'")
                sale_type_key_form = st.text_input("Sale Type Key*", help="Uppercase identifier, e.g., 'WEEKLY', 'SPECIAL'. No spaces/special chars except underscore.")
                sale_type_display_name_form = st.text_input("Sale Type Display Name*", help="e.g., 'Weekly Deals'. Appears in parentheses.")

                language_form = st.selectbox("Language*", ["english", "spanish"], key="new_store_lang_perm") # Unique key for permanent
                original_example_form = st.text_area("Original Example Caption*", height=100, help="A typical caption for this sale type.")
                date_format_form = st.text_input("Date Format*", help="e.g., 'MM/DD-MM/DD'. Leave blank for non-sale posts.")
                duration_text_pattern_form = st.text_input("Duration Text Pattern (Optional)", help="e.g., '3 DAYS ONLY', 'Sale Ends Sunday'")
                location_form = st.text_input("Location*", help="Store address or general area.")
                base_hashtags_form = st.text_input("Base Hashtags*", help="Comma-separated, e.g., #MyStore,#Deals")

                submitted_new_store = st.form_submit_button("💾 Save New Store Definition")

                if submitted_new_store:
                    if not all([store_name_form, sale_type_key_form, sale_type_display_name_form, language_form, original_example_form, location_form, base_hashtags_form]):
                        st.error("Please fill in all required (*) fields. Date Format can be blank.")
                    else:
                        store_key = re.sub(r'[^A-Z0-9_]', '', store_name_form.upper().replace(" ", "_"))
                        sale_type_key = re.sub(r'[^A-Z0-9_]', '', sale_type_key_form.upper())

                        if not store_key or not sale_type_key:
                            st.error("Store Name and Sale Type Key must result in valid identifiers.")
                        else:
                            new_sale_type_details = {
                                'id': f"{store_key.lower()}_{sale_type_key.lower()}",
                                'name': f"{store_name_form.strip()} ({sale_type_display_name_form.strip()})",
                                'language': language_form,
                                'original_example': original_example_form,
                                'defaultProduct': "",
                                'defaultPrice': "",
                                'dateFormat': date_format_form,
                                'durationTextPattern': duration_text_pattern_form,
                                'location': location_form,
                                'baseHashtags': base_hashtags_form
                            }

                            if not isinstance(st.session_state.get('custom_base_captions'), dict):
                                st.session_state.custom_base_captions = {}

                            if store_key not in st.session_state.custom_base_captions:
                                st.session_state.custom_base_captions[store_key] = {}

                            st.session_state.custom_base_captions[store_key][sale_type_key] = new_sale_type_details

                            try:
                                with open(CUSTOM_STORES_FILE, 'w') as f:
                                    json.dump(st.session_state.custom_base_captions, f, indent=4)
                                st.success(f"Store '{store_name_form}' saved!")
                            except IOError as e:
                                st.error(f"Error saving to {CUSTOM_STORES_FILE}: {e}.")

                            st.rerun()

        st.markdown("---")
        st.caption(f"Caption Gen v4.3 // {datetime.date.today().strftime('%Y-%m-%d')}")


    # --- File Uploader ---
    uploaded_file_objects = st.file_uploader(
        "Upload Image(s) or Video(s) of Grocery Sale Ads",
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "avi"],
        accept_multiple_files=True, key=f"uploader_{st.session_state.get('uploader_key_suffix', 0)}"
    )

    if uploaded_file_objects:
        new_files_info = []
        existing_file_signatures = {(f_info['name'], len(f_info['bytes'])) for f_info in st.session_state.uploaded_files_info}

        with st.spinner("Processing new uploads..."):
            for uploaded_file in uploaded_file_objects:
                file_bytes = uploaded_file.getvalue()
                if (uploaded_file.name, len(file_bytes)) not in existing_file_signatures:
                    file_info_dict = {
                        "name": uploaded_file.name,
                        "type": uploaded_file.type,
                        "bytes": file_bytes,
                        "display_thumbnail_bytes": None
                    }

                    if 'video' in uploaded_file.type:
                        file_info_dict['display_thumbnail_bytes'] = get_video_thumbnail(file_bytes)
                    else:
                        file_info_dict['display_thumbnail_bytes'] = file_bytes

                    if file_info_dict['display_thumbnail_bytes'] is None and 'video' in uploaded_file.type:
                        st.warning(f"Could not generate thumbnail for video '{uploaded_file.name}'.")
                        new_files_info.append(file_info_dict)
                    elif file_info_dict['display_thumbnail_bytes'] is not None :
                         new_files_info.append(file_info_dict)
                    else:
                        st.warning(f"Could not process and display '{uploaded_file.name}'. File skipped.")


        if new_files_info:
            st.session_state.uploaded_files_info.extend(new_files_info)
            st.session_state.analyzed_image_data_set = []
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
            st.session_state.last_caption_by_store = {}
            st.session_state.info_message_after_action = f"{len(new_files_info)} new file(s) added. Analysis cleared."
            st.rerun()

    # --- Action Buttons & File Previews ---
    if st.session_state.uploaded_files_info:
        action_cols = st.columns(2)
        analyze_button_disabled = st.session_state.is_analyzing_images or not st.session_state.uploaded_files_info

        if action_cols[0].button("Analyze Uploaded File(s)", disabled=analyze_button_disabled, type="primary", use_container_width=True):
            st.session_state.is_analyzing_images = True
            st.session_state.analyzed_image_data_set = []
            st.session_state.error_message = ""
            st.session_state.last_caption_by_store = {}
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
            st.rerun()

        action_cols[1].button("🗑️ Remove All & Clear Data", key="remove_all_images_button", on_click=handle_remove_all_images, use_container_width=True, type="secondary")

        with st.expander("Show Uploaded File Previews", expanded=True):
            previews_per_row = 4
            for i in range(0, len(st.session_state.uploaded_files_info), previews_per_row):
                cols = st.columns(previews_per_row)
                row_files_batch = st.session_state.uploaded_files_info[i : i + previews_per_row]
                for j, file_info in enumerate(row_files_batch):
                    actual_file_index = i + j
                    with cols[j]:
                        if 'video' in file_info['type']:
                            st.video(file_info['bytes'])
                            st.caption(file_info['name'])
                        elif file_info['display_thumbnail_bytes']:
                            st.image(file_info['display_thumbnail_bytes'], caption=file_info['name'], use_container_width=True)
                        else:
                            st.caption(f"{file_info['name']} (Preview not available)")

                        st.button("❌ Remove", key=f"remove_btn_{actual_file_index}_{file_info['name']}", on_click=remove_file_at_index, args=(actual_file_index,), use_container_width=True, type="secondary")
                for k_empty in range(len(row_files_batch), previews_per_row): cols[k_empty].container(height=50)
        st.markdown("---")


    # --- File Analysis Logic ---
    if st.session_state.is_analyzing_images and st.session_state.uploaded_files_info:
        with st.spinner("Analyzing files... This may take a few moments. Videos can take longer."):
            progress_bar = st.progress(0)
            total_files = len(st.session_state.uploaded_files_info)
            temp_analysis_results = []
            current_image_analysis_prompt = IMAGE_ANALYSIS_PROMPT_TEMPLATE

            for idx, file_info in enumerate(st.session_state.uploaded_files_info):
                progress_text = f"Analyzing {file_info['name']} ({idx+1}/{total_files})..."
                progress_bar.text(progress_text)
                progress_bar.progress((idx + 1) / total_files)

                analysis_data_item = {
                    "id": f"file-{file_info['name']}-{idx}",
                    "original_filename": file_info['name'],
                    "image_bytes_for_preview": file_info['display_thumbnail_bytes'],
                    "itemProduct": "", "itemCategory": "N/A",
                    "detectedBrands": "N/A", "selectedStoreKey": st.session_state.global_selected_store_key,
                    "selectedPriceFormat": PREDEFINED_PRICES[1]['value'] if PREDEFINED_PRICES and len(PREDEFINED_PRICES) > 1 else (PREDEFINED_PRICES[0]['value'] if PREDEFINED_PRICES else "CUSTOM"),
                    "itemPriceValue": "", "customItemPrice": "",
                    "dateRange": {"start": datetime.date.today().strftime("%Y-%m-%d"), "end": (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")},
                    "generatedCaption": "", "analysisError": "", "batch_selected": False
                }

                try:
                    analysis_text = ""
                    file_type = file_info.get('type', '')

                    if 'video' in file_type:
                        analysis_text = analyze_video_frames(VISION_MODEL, file_info['bytes'], current_image_analysis_prompt)
                    else:
                        analysis_text = analyze_image_with_gemini(VISION_MODEL, file_info['bytes'], current_image_analysis_prompt)

                    analysis_data_item['itemProduct'] = extract_field(r"^Product Name: (.*)$", analysis_text, default="Unknown Product").title()
                    analysis_data_item['itemCategory'] = extract_field(r"^Product Category: (.*)$", analysis_text, default="General Grocery")
                    analysis_data_item['detectedBrands'] = extract_field(r"^Detected Brands/Logos: (.*)$", analysis_text, default="N/A")

                    extracted_price_str = extract_field(r"^Price: (.*)$", analysis_text)
                    if extracted_price_str and extracted_price_str.lower() not in ["not found", "n/a"]:
                        found_format = False
                        for p_format in PREDEFINED_PRICES:
                            if p_format['value'] == "CUSTOM": continue
                            unit_part_match_condition = False
                            if p_format['value'] == "X for $Y":
                                if "for" in extracted_price_str.lower() and ("$" in extracted_price_str or "¢" in extracted_price_str):
                                    unit_part_match_condition = True
                            elif " " in p_format['value']:
                                if p_format['value'].split(" ", 1)[1].lower() in extracted_price_str.lower():
                                    unit_part_match_condition = True
                            else:
                                if p_format['value'].lower() in extracted_price_str.lower():
                                    unit_part_match_condition = True
                            if unit_part_match_condition:
                                analysis_data_item['selectedPriceFormat'] = p_format['value']
                                if p_format['value'] == "X for $Y":
                                    analysis_data_item['itemPriceValue'] = extracted_price_str
                                else:
                                    price_val_match = re.search(r"([\d\.]+)", extracted_price_str)
                                    if price_val_match:
                                        analysis_data_item['itemPriceValue'] = price_val_match.group(1)
                                    else:
                                        analysis_data_item['selectedPriceFormat'] = "CUSTOM"
                                        analysis_data_item['customItemPrice'] = extracted_price_str
                                found_format = True; break
                        if not found_format:
                            analysis_data_item['selectedPriceFormat'] = "CUSTOM"
                            analysis_data_item['customItemPrice'] = extracted_price_str
                    else:
                        analysis_data_item['selectedPriceFormat'] = "CUSTOM"
                        analysis_data_item['customItemPrice'] = "N/A"

                    detected_store_name = extract_field(r"^Store Name: (.*)$", analysis_text)
                    if detected_store_name and detected_store_name.lower() not in ["n/a", "not found"]:
                        matched_key = find_store_key_by_name(detected_store_name, current_combined_captions)
                        if matched_key:
                            analysis_data_item['selectedStoreKey'] = matched_key
                        else:
                            analysis_data_item['analysisError'] += f"Store '{detected_store_name}' not in predefined list. Defaulting. "

                    dates_str = extract_field(r"^Sale Dates: (.*)$", analysis_text)
                    if dates_str and dates_str.lower() not in ["n/a", "not found"]:
                        date_parts = re.split(r'\s+to\s+|\s*-\s*|\s*–\s*', dates_str)
                        parsed_start, parsed_end = None, None
                        if len(date_parts) >= 1:
                            parsed_start = try_parse_date_from_image_text(date_parts[0])
                        if len(date_parts) >= 2:
                            end_part_text = date_parts[1]
                            if re.fullmatch(r"\d{1,2}", end_part_text.strip()) and parsed_start:
                                try:
                                    start_dt_obj = datetime.datetime.strptime(parsed_start, "%Y-%m-%d").date()
                                    end_day_num = int(end_part_text.strip())
                                    month_to_use, year_to_use = start_dt_obj.month, start_dt_obj.year
                                    if start_dt_obj.day > end_day_num:
                                        month_to_use = (start_dt_obj.month % 12) + 1
                                        if month_to_use == 1 and start_dt_obj.month == 12:
                                            year_to_use += 1
                                    end_part_text_for_parse = f"{month_to_use}/{end_day_num}"
                                    if year_to_use != datetime.date.today().year:
                                         end_part_text_for_parse += f"/{year_to_use % 100}"
                                    parsed_end = try_parse_date_from_image_text(end_part_text_for_parse)
                                except ValueError:
                                    parsed_end = try_parse_date_from_image_text(end_part_text)
                            else:
                                parsed_end = try_parse_date_from_image_text(end_part_text)
                        if parsed_start:
                            analysis_data_item['dateRange']['start'] = parsed_start
                        if parsed_end:
                            analysis_data_item['dateRange']['end'] = parsed_end
                        s_dt_str = analysis_data_item['dateRange']['start']
                        e_dt_str = analysis_data_item['dateRange']['end']
                        try:
                            s_dt = datetime.datetime.strptime(s_dt_str, "%Y-%m-%d").date()
                            e_dt = datetime.datetime.strptime(e_dt_str, "%Y-%m-%d").date()
                            if s_dt > e_dt:
                                analysis_data_item['dateRange']['start'], analysis_data_item['dateRange']['end'] = e_dt_str, s_dt_str
                                analysis_data_item['analysisError'] += "Start/End dates reordered. "
                            if parsed_start and not parsed_end:
                                analysis_data_item['dateRange']['end'] = (s_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                                analysis_data_item['analysisError'] += "End date inferred (1 day after start). Review. "
                            elif not parsed_start and parsed_end:
                                analysis_data_item['analysisError'] += "Start date not found. Using today. Review. "
                        except ValueError:
                            analysis_data_item['analysisError'] += "Date parsing error. Defaults used. "
                            analysis_data_item['dateRange']['start'] = datetime.date.today().strftime("%Y-%m-%d")
                            analysis_data_item['dateRange']['end'] = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
                    else:
                        analysis_data_item['analysisError'] += "Sale dates not found. Defaults used. "
                except Exception as e:
                    analysis_data_item['analysisError'] += f"Analysis exception: {str(e)}. Review manually. "
                temp_analysis_results.append(analysis_data_item)

            st.session_state.analyzed_image_data_set = temp_analysis_results
            st.session_state.analyzed_image_data_set_source_length = len(st.session_state.uploaded_files_info)
            progress_bar.empty()
            st.session_state.is_analyzing_images = False
            st.success(f"✅ File analysis complete for {len(temp_analysis_results)} file(s). Review below.")
            st.rerun()


    # --- Batch Caption Generation ---
    if st.session_state.analyzed_image_data_set and not st.session_state.is_analyzing_images:
        items_selected_for_batch = any(item.get('batch_selected', False) for item in st.session_state.analyzed_image_data_set)
        if st.button("✍️ Generate Captions for Selected Items", type="primary", use_container_width=True,
                      disabled=st.session_state.is_batch_generating_captions or not items_selected_for_batch):
            st.session_state.is_batch_generating_captions = True
            generated_count = 0
            items_to_process_by_store = {}
            for index, data_item_loop_var in enumerate(st.session_state.analyzed_image_data_set):
                if data_item_loop_var.get('batch_selected', False):
                    store_key = data_item_loop_var['selectedStoreKey']
                    if store_key not in items_to_process_by_store:
                        items_to_process_by_store[store_key] = []
                    items_to_process_by_store[store_key].append(index)

            with st.spinner("Generating captions for selected items... This can take a while for many items."):
                for store_key_for_batch, item_indices in items_to_process_by_store.items():
                    reference_caption_for_current_store_batch = st.session_state.last_caption_by_store.get(store_key_for_batch)
                    for index_in_session_state in item_indices:
                        current_data_item_ref = st.session_state.analyzed_image_data_set[index_in_session_state]
                        exec_single_item_generation(index_in_session_state)
                        if current_data_item_ref.get('generatedCaption'):
                            generated_count +=1
                            if not reference_caption_for_current_store_batch:
                                reference_caption_for_current_store_batch = current_data_item_ref['generatedCaption']
                            st.session_state.last_caption_by_store[store_key_for_batch] = current_data_item_ref['generatedCaption']


            st.session_state.is_batch_generating_captions = False
            if generated_count > 0:
                st.success(f"Successfully generated captions for {generated_count} selected item(s).")
            else:
                st.info("No captions were generated in this batch (check errors or selection).")
            st.rerun()


    # --- Individual Item Details & Caption Generation ---
    if st.session_state.analyzed_image_data_set:
        if not st.session_state.is_batch_generating_captions and st.session_state.uploaded_files_info :
            st.markdown("---")
            st.header("File Details & Caption Generation")

            # --- Select/Deselect All Buttons ---
            action_cols = st.columns(8)
            if action_cols[0].button("Select All", use_container_width=True, key="select_all_btn"):
                for item in st.session_state.analyzed_image_data_set:
                    item['batch_selected'] = True
                st.rerun()

            if action_cols[1].button("Deselect All", use_container_width=True, key="deselect_all_btn"):
                for item in st.session_state.analyzed_image_data_set:
                    item['batch_selected'] = False
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            # --- End Select/Deselect All ---

        for index, data_item_proxy in enumerate(st.session_state.analyzed_image_data_set):
            item_key_prefix = f"item_{data_item_proxy['id']}"
            data_item = st.session_state.analyzed_image_data_set[index]

            with st.container(border=True):
                data_item['batch_selected'] = st.checkbox("Select for Batch Generation", value=data_item.get('batch_selected', False), key=f"{item_key_prefix}_batch_select")
                st.markdown(f"##### File: **{data_item.get('original_filename', data_item['id'])}**")
                if data_item.get('analysisError'):
                    st.warning(f"💡 Notes/Errors: {data_item['analysisError']}")

                col1, col2 = st.columns([1, 2])

                with col1:
                    if data_item['image_bytes_for_preview']:
                        st.image(data_item['image_bytes_for_preview'], use_container_width=True)
                    else:
                        st.caption("Preview N/A")


                with col2:
                    # This section remains largely the same, letting users edit data
                    new_prod = st.text_input("Product Name", value=data_item.get('itemProduct', ''), key=f"{item_key_prefix}_prod_ind")
                    if new_prod != data_item.get('itemProduct', ''): data_item['itemProduct'] = new_prod; st.rerun()

                    new_cat = st.text_input("Product Category", value=data_item.get('itemCategory', 'N/A'), key=f"{item_key_prefix}_cat_ind")
                    if new_cat != data_item.get('itemCategory', 'N/A'): data_item['itemCategory'] = new_cat; st.rerun()

                    new_brands = st.text_input("Detected Brands", value=data_item.get('detectedBrands', 'N/A'), key=f"{item_key_prefix}_brands_ind", help="Comma-separated")
                    if new_brands != data_item.get('detectedBrands', 'N/A'): data_item['detectedBrands'] = new_brands; st.rerun()

                    store_options_map = { k: (v[list(v.keys())[0]]['name'].split('(')[0].strip() if v and list(v.keys()) else k.replace('_', ' ')) or k.replace('_', ' ') for k, v in current_combined_captions.items()}
                    current_store_key = data_item.get('selectedStoreKey', st.session_state.global_selected_store_key)
                    if not current_combined_captions: st.warning("No stores defined!")
                    elif current_store_key not in store_options_map:
                        current_store_key = list(store_options_map.keys())[0] if store_options_map else None
                        data_item['selectedStoreKey'] = current_store_key
                    if current_combined_captions:
                        try:
                            valid_keys = list(store_options_map.keys())
                            store_idx = valid_keys.index(current_store_key) if current_store_key in valid_keys else 0
                        except ValueError: store_idx = 0
                        selected_store_display_name = st.selectbox("Store", options=list(store_options_map.values()), index=store_idx, key=f"{item_key_prefix}_store_ind")
                        new_selected_store_key = next((k for k, v_disp in store_options_map.items() if v_disp == selected_store_display_name), current_store_key)
                        if new_selected_store_key != data_item.get('selectedStoreKey'):
                            data_item['selectedStoreKey'] = new_selected_store_key; st.rerun()
                    else: st.text("No stores available to select.")

                    # Get the caption structure to conditionally show price/date fields
                    temp_store_key = data_item.get('selectedStoreKey')
                    temp_store_info = current_combined_captions.get(temp_store_key, {})
                    temp_sub_key = list(temp_store_info.keys())[0] if temp_store_info else None
                    temp_caption_structure = temp_store_info.get(temp_sub_key, {})
                    is_sale_based_ui = temp_caption_structure.get('dateFormat') != ""

                    if is_sale_based_ui:
                        price_fmt_map = {p['value']: p['label'] for p in PREDEFINED_PRICES}
                        current_price_format = data_item.get('selectedPriceFormat', PREDEFINED_PRICES[1]['value'] if PREDEFINED_PRICES and len(PREDEFINED_PRICES) > 1 else (PREDEFINED_PRICES[0]['value'] if PREDEFINED_PRICES else "CUSTOM"))
                        if PREDEFINED_PRICES:
                            try: p_fmt_idx = list(price_fmt_map.keys()).index(current_price_format)
                            except ValueError: p_fmt_idx = 1 if len(PREDEFINED_PRICES) > 1 else 0
                            selected_price_format_val = st.selectbox("Price Format", options=list(price_fmt_map.keys()), format_func=lambda x: price_fmt_map[x], index=p_fmt_idx, key=f"{item_key_prefix}_pfmt_ind")
                            if selected_price_format_val != data_item.get('selectedPriceFormat'):
                                data_item['selectedPriceFormat'] = selected_price_format_val; st.rerun()
                            if selected_price_format_val == "CUSTOM":
                                new_custom_p = st.text_input("Custom Price Text", value=data_item.get('customItemPrice', ''), key=f"{item_key_prefix}_pcustom_ind")
                                if new_custom_p != data_item.get('customItemPrice', ''): data_item['customItemPrice'] = new_custom_p; st.rerun()
                            elif selected_price_format_val == "X for $Y":
                                new_xfory_p = st.text_input("Price (e.g., 2 for $5.00)", value=data_item.get('itemPriceValue', ''), key=f"{item_key_prefix}_pxfory_ind")
                                if new_xfory_p != data_item.get('itemPriceValue', ''): data_item['itemPriceValue'] = new_xfory_p; st.rerun()
                            else:
                                new_pval = st.text_input("Price Value (e.g., 1.99 or 79)", value=data_item.get('itemPriceValue', ''), key=f"{item_key_prefix}_pval_ind")
                                if new_pval != data_item.get('itemPriceValue', ''): data_item['itemPriceValue'] = new_pval; st.rerun()
                        else: st.text("No price formats defined.")

                        date_c1, date_c2 = st.columns(2)
                        with date_c1:
                            try: s_dt_val = datetime.datetime.strptime(data_item['dateRange']['start'], "%Y-%m-%d").date()
                            except: s_dt_val = datetime.date.today()
                            new_s_dt = st.date_input("Start Date", value=s_dt_val, key=f"{item_key_prefix}_sdate_ind")
                            if new_s_dt.strftime("%Y-%m-%d") != data_item['dateRange']['start']:
                                data_item['dateRange']['start'] = new_s_dt.strftime("%Y-%m-%d"); st.rerun()
                        with date_c2:
                            try: e_dt_val = datetime.datetime.strptime(data_item['dateRange']['end'], "%Y-%m-%d").date()
                            except: e_dt_val = datetime.date.today() + datetime.timedelta(days=6)
                            current_start_date_for_end_picker = datetime.datetime.strptime(data_item['dateRange']['start'], "%Y-%m-%d").date()
                            new_e_dt = st.date_input("End Date", value=e_dt_val, key=f"{item_key_prefix}_edate_ind", min_value=current_start_date_for_end_picker)
                            if new_e_dt.strftime("%Y-%m-%d") != data_item['dateRange']['end']:
                                data_item['dateRange']['end'] = new_e_dt.strftime("%Y-%m-%d"); st.rerun()

                caption_loading_key = f"{item_key_prefix}_caption_loading_ind"
                if caption_loading_key not in st.session_state: st.session_state[caption_loading_key] = False
                if st.button(f"✍️ Generate Caption for this Item", key=f"{item_key_prefix}_gen_btn_ind",
                              disabled=st.session_state[caption_loading_key] or st.session_state.is_batch_generating_captions,
                              type="secondary", use_container_width=True):

                    st.session_state[caption_loading_key] = True
                    # Re-use the batch generation logic for a single item
                    exec_single_item_generation(index) # Use a helper to avoid code duplication
                    st.session_state[caption_loading_key] = False
                    st.rerun()

                if st.session_state[caption_loading_key]:
                    st.caption("⏳ Generating caption for this item...")

                if data_item.get('generatedCaption'):
                    caption_text_to_display = data_item['generatedCaption']
                    st.text_area("📝 Generated Caption:", value=caption_text_to_display, height=200, key=f"{item_key_prefix}_capt_out_display_ind", help="Review and copy below.")
                    text_area_id = f"copytext_{item_key_prefix}_ind"; feedback_span_id = f"copyfeedback_{item_key_prefix}_ind"
                    escaped_caption_for_html = html_escaper.escape(caption_text_to_display)
                    copy_button_html_content = f"""<textarea id="{text_area_id}" style="opacity:0.01; height:1px; width:1px; position:absolute; z-index: -1; pointer-events:none;" readonly>{escaped_caption_for_html}</textarea><button onclick="copyToClipboard('{text_area_id}', '{feedback_span_id}')" style="padding: 0.25rem 0.75rem; margin-top: 5px; border-radius: 8px; border: 1px solid #4A4D56; background-color: #262730; color: #FAFAFA; cursor:pointer;">📋 Copy Caption</button><span id="{feedback_span_id}" style="margin-left: 10px; font-size: 0.9em;"></span><script>if(typeof window.copyToClipboard !== 'function'){{window.copyToClipboard=function(elementId,feedbackId){{var copyText=document.getElementById(elementId);var feedbackSpan=document.getElementById(feedbackId);if(!copyText||!feedbackSpan){{if(feedbackSpan)feedbackSpan.innerText="Error: Elements missing.";return;}}copyText.style.display='block';copyText.select();copyText.setSelectionRange(0,99999);copyText.style.display='none';var msg="";try{{var successful=document.execCommand('copy');msg=successful?'Copied!':'Copy failed.';}}catch(err){{msg='Oops, unable to copy.';}}feedbackSpan.innerText=msg;setTimeout(function(){{feedbackSpan.innerText='';}},2500);}}}}</script>"""
                    st_html_component(copy_button_html_content, height=45)
            st.markdown("---")

    else:
        if not st.session_state.is_analyzing_images and not st.session_state.uploaded_files_info:
            st.info("☝️ Upload some image or video files of grocery sale ads to get started, or add a new store definition via the sidebar!")

def exec_single_item_generation(index):
    """Helper function to run caption generation logic for a single item to reduce code duplication."""
    current_combined_captions = get_combined_captions()
    data_item = st.session_state.analyzed_image_data_set[index]
    data_item['generatedCaption'] = ""
    store_details_key = data_item['selectedStoreKey']
    store_info_set = current_combined_captions.get(store_details_key)
    current_error = data_item.get('analysisError', "")

    if not store_info_set:
        current_error += f" Store details for '{store_details_key}' not found."
    else:
        sale_detail_sub_key = list(store_info_set.keys())[0]
        if store_details_key == 'TEDS_FRESH_MARKET':
            day_for_teds = get_current_day_for_teds()
            if day_for_teds == 2 and 'THREE_DAY' in store_info_set: sale_detail_sub_key = 'THREE_DAY'
            elif day_for_teds == 5 and 'FOUR_DAY' in store_info_set: sale_detail_sub_key = 'FOUR_DAY'
            elif sale_detail_sub_key not in store_info_set: sale_detail_sub_key = list(store_info_set.keys())[0]

        caption_structure = store_info_set.get(sale_detail_sub_key)
        if not caption_structure:
            current_error += f" Caption structure for '{sale_detail_sub_key}' under '{store_details_key}' not found."
        else:
            is_sale_based_post = caption_structure.get('dateFormat') != ""

            product_display_text = data_item.get('itemProduct', 'Unknown Product')
            if not product_display_text.strip() or product_display_text == "Unknown Product":
                current_error += " Product name missing/unknown."

            final_price = get_final_price_string(data_item['selectedPriceFormat'], data_item['itemPriceValue'], data_item['customItemPrice'])
            if is_sale_based_post and (not final_price or "[Price Value]" in final_price or "[Custom Price]" in final_price or "[X for $Y Price]" in final_price or "N/A" in final_price):
                current_error += " Invalid/missing price."


            display_dates = ""
            if is_sale_based_post:
                display_dates = format_dates_for_caption_context(data_item['dateRange']['start'], data_item['dateRange']['end'], caption_structure['dateFormat'], caption_structure['language'])
                if "MISSING" in display_dates or "INVALID" in display_dates:
                    if "Invalid date range for caption." not in current_error:
                        current_error += " Invalid date range for caption."


            holiday_ctx = get_holiday_context(data_item['dateRange']['start'], data_item['dateRange']['end']) if is_sale_based_post else ""
            prompt_list = [f"Generate a social media caption for a grocery store promotion.", f"Store & Sale Type: {caption_structure['name']}"]

            detected_brands = data_item.get('detectedBrands', 'N/A')
            temp_product_display_text = product_display_text
            if detected_brands.lower() not in ['n/a', 'not found', '']: temp_product_display_text += f" (featuring {detected_brands})"

            prompt_list.append(f"Product to feature: {temp_product_display_text}")

            if is_sale_based_post:
                prompt_list.append(f"Price: {final_price}")
                if "MISSING" not in display_dates and "INVALID" not in display_dates:
                    prompt_list.append(f"Sale Dates (for display in caption): {display_dates}. (Actual period: {data_item['dateRange']['start']} to {data_item['dateRange']['end']}).")

            if holiday_ctx: prompt_list.append(f"Relevant Holiday Context: {holiday_ctx}.")

            prompt_list.extend([
                f"Store Location: {caption_structure['location']}.",
                f"Language for caption: {caption_structure['language']}.",
                f"Desired Tone: {st.session_state.global_selected_tone}."
            ])

            if holiday_ctx and st.session_state.global_selected_tone == "Seasonal / Festive":
                prompt_list.append(f"Strongly emphasize the {holiday_ctx} theme and use relevant emojis.")

            reference_caption_for_store = st.session_state.last_caption_by_store.get(store_details_key)
            if reference_caption_for_store:
                prompt_list.extend([f"\nIMPORTANT STYLISTIC NOTE: For consistency with other posts for this store, please try to follow a similar structure, tone, and overall style to the following reference caption. Adapt product details, price, and specific emojis for the current item, but keep the general formatting and sentence flow consistent with the reference.", f"REFERENCE CAPTION START:\n{reference_caption_for_store}\nREFERENCE CAPTION END\nWhen generating the new caption, please provide a creative and different alternative to the reference caption."])

            prompt_list.extend([f"\nReference Style (from original example - adapt, don't copy verbatim, especially if a continuity reference above is provided):\n\"{caption_structure['original_example']}\"", "\nCaption Requirements:", "- Unique, engaging, ready for social media."])

            if is_sale_based_post:
                prompt_list.append(f"- Feature the product on sale by stating its name (and brand like '{detected_brands}' if relevant and not 'N/A') immediately followed by or closely linked to its price. For example: '{temp_product_display_text} is now {final_price}!'. Also, clearly include the store location.")
                if "MISSING" not in display_dates and "INVALID" not in display_dates:
                    prompt_list.append(f"- Clearly include the sale dates (as per 'display_dates').")
            else:
                prompt_list.append(f"- Feature the product by describing it in an appealing way, for example: 'Come try our delicious {temp_product_display_text} today!'. Do not mention price or sale dates.")

            prompt_list.append(f"- Incorporate relevant emojis for product, tone, and holiday ({holiday_ctx if is_sale_based_post else 'general appeal'}).")

            item_category_for_prompt = data_item.get('itemCategory', 'N/A'); base_hashtags = caption_structure['baseHashtags']; hashtag_details = [f"product-specific for '{product_display_text}'"]
            if item_category_for_prompt.lower() not in ['n/a', 'not found', '', 'general grocery']:
                hashtag_details.append(f"category '{item_category_for_prompt}'")
            prompt_list.append(f"- Include these base hashtags: {base_hashtags}. Add 2-3 creative hashtags. Also, 1-2 hashtags for each: {', '.join(hashtag_details)}.")

            prompt_list.extend([f"- Store's main name ({caption_structure['name'].split('(')[0].strip()}) should be prominent if location \"{caption_structure['location']}\" is just a city/area.", "- Good formatting with line breaks."])

            if is_sale_based_post and caption_structure.get('durationTextPattern') and "MISSING" not in display_dates and "INVALID" not in display_dates:
                prompt_list.append(f"- Naturally integrate promotional phrase \"{caption_structure['durationTextPattern']}\" with sale dates {display_dates} if it makes sense.")

            final_prompt_for_caption = "\n".join(prompt_list)
            try:
                generated_text = generate_caption_with_gemini(TEXT_MODEL, final_prompt_for_caption)
                cleaned_text = generated_text.replace('*', '')
                data_item['generatedCaption'] = cleaned_text
                st.session_state.last_caption_by_store[store_details_key] = cleaned_text
            except Exception as e:
                current_error += f" Caption API error: {str(e)}"

    data_item['analysisError'] = current_error.strip()

if __name__ == "__main__":
    main()
