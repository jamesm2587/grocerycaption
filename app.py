# app.py
import streamlit as st
import datetime
import io 
import re 

# Local imports
from config import VISION_MODEL, TEXT_MODEL 
from constants import INITIAL_BASE_CAPTIONS, TONE_OPTIONS, PREDEFINED_PRICES
from utils import (
    get_current_day_for_teds, get_holiday_context, format_dates_for_caption_context,
    get_final_price_string, find_store_key_by_name, try_parse_date_from_image_text
)
from gemini_services import analyze_image_with_gemini, generate_caption_with_gemini, extract_field


# --- Callback function for removing an uploaded file ---
def remove_file_at_index(index_to_remove):
    if 'uploaded_files_info' in st.session_state and \
       0 <= index_to_remove < len(st.session_state.uploaded_files_info):
        
        removed_file_name = st.session_state.uploaded_files_info[index_to_remove]['name']
        st.session_state.uploaded_files_info.pop(index_to_remove)
        
        # If analysis results exist, they are now potentially out of sync or invalid.
        # Simplest and most robust is to clear them, requiring re-analysis for the remaining set.
        if 'analyzed_image_data_set' in st.session_state and st.session_state.analyzed_image_data_set:
            st.session_state.analyzed_image_data_set = []
            # If you were tracking source length for complex sync, clear that too
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
            st.session_state.info_message_after_action = f"Image '{removed_file_name}' removed. Previous analysis results cleared. Please re-analyze the remaining images if needed."
        else:
            st.session_state.info_message_after_action = f"Image '{removed_file_name}' removed."
            
        # If no files are left, ensure analysis data is also cleared
        if not st.session_state.uploaded_files_info:
            st.session_state.analyzed_image_data_set = []
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
    # Streamlit's on_click for buttons automatically triggers a rerun.

# --- Streamlit App State Initialization ---
def initialize_session_state():
    defaults = {
        'analyzed_image_data_set': [],
        'global_selected_store_key': list(INITIAL_BASE_CAPTIONS.keys())[0] if INITIAL_BASE_CAPTIONS else None,
        'global_selected_tone': TONE_OPTIONS[0]['value'] if TONE_OPTIONS else None,
        'uploaded_files_info': [],
        'error_message': "",
        'is_analyzing_images': False,
        'info_message_after_action': "" # For messages like after removing a file
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Main App UI ---
def main():
    st.set_page_config(layout="wide", page_title="Caption Generator")
    st.title("✨ Social Media Caption Generator ✨")
    st.caption(f"Powered by Gemini API. Current Date: {datetime.date.today().strftime('%B %d, %Y')}")

    initialize_session_state() 

    if not VISION_MODEL or not TEXT_MODEL:
        st.error("🔴 Gemini Models not available. Please check configuration.")
        st.stop() 

    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = "" 

    # Display general info messages (e.g., after file removal)
    if st.session_state.info_message_after_action:
        st.info(st.session_state.info_message_after_action)
        st.session_state.info_message_after_action = "" # Clear after displaying


    # --- File Uploader ---
    uploaded_file_objects = st.file_uploader(
        "Upload Image(s) of Grocery Sale Ads", type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True, key="uploader"
    )

    if uploaded_file_objects:
        new_files_info = []
        # Get existing signatures to prevent re-adding identical files if user re-selects
        existing_file_signatures = {(f_info['name'], len(f_info['bytes'])) for f_info in st.session_state.uploaded_files_info}
        
        for uploaded_file in uploaded_file_objects:
            file_bytes = uploaded_file.getvalue()
            if (uploaded_file.name, len(file_bytes)) not in existing_file_signatures:
                new_files_info.append({"name": uploaded_file.name, "type": uploaded_file.type, "bytes": file_bytes})
        
        if new_files_info:
            # Append new, unique files to the existing list
            st.session_state.uploaded_files_info.extend(new_files_info)
            # Clear previous analysis results as the set of files has changed
            st.session_state.analyzed_image_data_set = []
            if 'analyzed_image_data_set_source_length' in st.session_state:
                del st.session_state.analyzed_image_data_set_source_length
            st.session_state.info_message_after_action = f"{len(new_files_info)} new image(s) added. Previous analysis results cleared. Click 'Analyze' to process all images."
            st.rerun() # Rerun to show new previews and the info message


    # --- Image Previews and Analyze Button ---
    if st.session_state.uploaded_files_info:
        st.subheader("Uploaded Image Previews:")
        
        previews_per_row = 5 
        for i in range(0, len(st.session_state.uploaded_files_info), previews_per_row):
            cols = st.columns(previews_per_row)
            row_files_batch = st.session_state.uploaded_files_info[i : i + previews_per_row]
            
            for j, file_info in enumerate(row_files_batch):
                actual_file_index = i + j 
                with cols[j]:
                    st.image(file_info['bytes'], caption=file_info['name'], use_container_width=True)
                    st.button(
                        "❌ Remove", 
                        key=f"remove_btn_{actual_file_index}_{file_info['name']}", # Key needs to be unique
                        on_click=remove_file_at_index, 
                        args=(actual_file_index,), 
                        use_container_width=True,
                        type="secondary"
                    )
            # Fill empty columns if the last row is not full
            for k_empty in range(len(row_files_batch), previews_per_row):
                with cols[k_empty]:
                    st.container(height=50) # Use st.container with a fixed height or st.empty for layout consistency

        st.markdown("---") # Separator before analyze button
        if st.button("👁️ Analyze Uploaded Image(s)", disabled=st.session_state.is_analyzing_images, type="primary", use_container_width=True):
            if not st.session_state.uploaded_files_info:
                st.warning("Please upload images before analyzing.")
            else:
                st.session_state.is_analyzing_images = True
                st.session_state.analyzed_image_data_set = [] 
                st.session_state.error_message = ""
                if 'analyzed_image_data_set_source_length' in st.session_state: # Clear old tracker
                    del st.session_state.analyzed_image_data_set_source_length
                st.rerun() 
    
    # --- Image Analysis Logic ---
    if st.session_state.is_analyzing_images and st.session_state.uploaded_files_info:
        with st.spinner("Analyzing images... This may take a few moments."):
            # (The rest of your analysis logic remains the same here)
            # ... (omitted for brevity, same as before) ...
            progress_bar = st.progress(0)
            total_files = len(st.session_state.uploaded_files_info)
            temp_analysis_results = []

            image_analysis_prompt_template = (
                "Analyze this grocery sale image. Extract all details precisely. "
                "Respond strictly in this format, ensuring each field is on a new line:\n"
                "Product Name: [Primary product name or names clearly featured for sale]\n"
                "Price: [Price of the primary product, including currency and unit, e.g., $1.99/lb, 2 for $5.00, 99¢ each]\n"
                "Sale Dates: [Sale period, e.g., MM/DD-MM/DD, Ends MM/DD, May 15-20. If year is present, include it.]\n"
                "Store Name: [Visible store name, if any]\n"
                "Promotional Text: [Any other relevant promotional phrases or taglines, like '3 Days Only', 'Special Offer']\n"
                "If a field is not found or unclear, state 'Not found' for that field and only that field."
            )

            for idx, file_info in enumerate(st.session_state.uploaded_files_info):
                progress_text = f"Analyzing {file_info['name']} ({idx+1}/{total_files})..."
                progress_bar.progress((idx + 1) / total_files, text=progress_text)
                
                analysis_data_item = {
                    "id": f"image-{file_info['name']}-{idx}", 
                    "original_filename": file_info['name'],
                    "image_bytes_for_preview": file_info['bytes'],
                    "itemProduct": "", "selectedStoreKey": st.session_state.global_selected_store_key,
                    "selectedPriceFormat": PREDEFINED_PRICES[1]['value'], "itemPriceValue": "", "customItemPrice": "",
                    "dateRange": {"start": datetime.date.today().strftime("%Y-%m-%d"), 
                                  "end": (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")},
                    "generatedCaption": "", "analysisError": ""
                }
                try:
                    analysis_text = analyze_image_with_gemini(VISION_MODEL, file_info['bytes'], image_analysis_prompt_template)
                    
                    analysis_data_item['itemProduct'] = extract_field(r"^Product Name: (.*)$", analysis_text)
                    
                    extracted_price_str = extract_field(r"^Price: (.*)$", analysis_text)
                    if extracted_price_str:
                        found_format = False
                        for p_format in PREDEFINED_PRICES:
                            if p_format['value'] == "CUSTOM": continue
                            unit_part_match_condition = False
                            if p_format['value'] == "X for $Y":
                                if "for" in extracted_price_str.lower() and ("$" in extracted_price_str or "¢" in extracted_price_str):
                                    unit_part_match_condition = True
                            elif " " in p_format['value']: 
                                unit_part = p_format['value'].split(" ", 1)[1].lower()
                                if unit_part in extracted_price_str.lower():
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
                                found_format = True
                                break
                        if not found_format:
                            analysis_data_item['selectedPriceFormat'] = "CUSTOM"
                            analysis_data_item['customItemPrice'] = extracted_price_str
                    
                    detected_store_name = extract_field(r"^Store Name: (.*)$", analysis_text)
                    if detected_store_name:
                        matched_key = find_store_key_by_name(detected_store_name, INITIAL_BASE_CAPTIONS)
                        if matched_key: analysis_data_item['selectedStoreKey'] = matched_key
                        else: analysis_data_item['analysisError'] += f"Store '{detected_store_name}' not in predefined list. Defaulting. "

                    dates_str = extract_field(r"^Sale Dates: (.*)$", analysis_text)
                    if dates_str:
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
                                    month_to_use = start_dt_obj.month
                                    year_to_use = start_dt_obj.year
                                    if start_dt_obj.day > end_day_num : 
                                        month_to_use = (start_dt_obj.month % 12) + 1
                                        if month_to_use == 1: year_to_use +=1 
                                    
                                    end_part_text_for_parse = f"{month_to_use}/{end_day_num}"
                                    if year_to_use != datetime.date.today().year:
                                         end_part_text_for_parse += f"/{year_to_use % 100}"
                                    parsed_end = try_parse_date_from_image_text(end_part_text_for_parse)
                                except ValueError: 
                                    parsed_end = try_parse_date_from_image_text(end_part_text) 
                            else: 
                                parsed_end = try_parse_date_from_image_text(end_part_text)
                        
                        if parsed_start: analysis_data_item['dateRange']['start'] = parsed_start
                        if parsed_end: analysis_data_item['dateRange']['end'] = parsed_end
                        
                        s_dt_str, e_dt_str = analysis_data_item['dateRange']['start'], analysis_data_item['dateRange']['end']
                        try:
                            s_dt = datetime.datetime.strptime(s_dt_str, "%Y-%m-%d").date()
                            e_dt = datetime.datetime.strptime(e_dt_str, "%Y-%m-%d").date()

                            if s_dt > e_dt: 
                                analysis_data_item['dateRange']['start'], analysis_data_item['dateRange']['end'] = e_dt_str, s_dt_str
                                analysis_data_item['analysisError'] += "Start/End dates reordered. "
                            
                            if parsed_start and not parsed_end:
                                inferred_end_dt = (s_dt + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
                                analysis_data_item['dateRange']['end'] = inferred_end_dt
                                analysis_data_item['analysisError'] += "End date inferred. "
                            elif not parsed_start and parsed_end:
                                inferred_start_dt = (e_dt - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
                                analysis_data_item['dateRange']['start'] = inferred_start_dt
                                analysis_data_item['analysisError'] += "Start date inferred. "
                        except ValueError: 
                            analysis_data_item['analysisError'] += "Date parsing error. Using default dates. "
                            analysis_data_item['dateRange']['start'] = datetime.date.today().strftime("%Y-%m-%d")
                            analysis_data_item['dateRange']['end'] = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
                except Exception as e:
                    analysis_data_item['analysisError'] += f"Analysis exception: {str(e)}. Please review fields manually. "
                
                temp_analysis_results.append(analysis_data_item)
            
            st.session_state.analyzed_image_data_set = temp_analysis_results
            # Track the source length for potential future sync logic if needed
            st.session_state.analyzed_image_data_set_source_length = len(st.session_state.uploaded_files_info) 
            progress_bar.empty()
            st.session_state.is_analyzing_images = False
            st.success(f"✅ Image analysis complete for {len(temp_analysis_results)} image(s). Review and generate captions below.")
            st.rerun()


    # --- Sidebar for Global Settings ---
    # (No changes here, same as before)
    # ...
    st.sidebar.header("Global Settings")
    tone_labels_dict = {tone['value']: tone['label'] for tone in TONE_OPTIONS}
    current_global_tone = st.session_state.get('global_selected_tone', TONE_OPTIONS[0]['value'])
    if current_global_tone not in tone_labels_dict:
        current_global_tone = TONE_OPTIONS[0]['value']
        st.session_state.global_selected_tone = current_global_tone

    selected_tone_val = st.sidebar.selectbox(
        "Caption Tone", options=list(tone_labels_dict.keys()),
        format_func=lambda x: tone_labels_dict[x],
        index=list(tone_labels_dict.keys()).index(current_global_tone),
        key="global_tone_selector"
    )
    if selected_tone_val and selected_tone_val != st.session_state.global_selected_tone:
         st.session_state.global_selected_tone = selected_tone_val


    # --- Display Analyzed Data & Generate Captions ---
    # (No functional changes here, but it will now correctly react to an empty analyzed_image_data_set if cleared)
    # ...
    if st.session_state.analyzed_image_data_set:
        st.markdown("---")
        st.header("📄 Image Details & Caption Generation")
        
        for index, data_item_proxy in enumerate(st.session_state.analyzed_image_data_set):
            item_key_prefix = f"item_{data_item_proxy['id']}"
            data_item = st.session_state.analyzed_image_data_set[index] 

            with st.container(border=True):
                st.markdown(f"##### Image: **{data_item.get('original_filename', data_item['id'])}**")
                if data_item.get('analysisError'): st.warning(f"💡 Notes/Errors: {data_item['analysisError']}")

                col1, col2 = st.columns([1, 2])
                with col1: st.image(data_item['image_bytes_for_preview'], use_container_width=True)
                
                with col2:
                    new_prod = st.text_input("Product Name", value=data_item.get('itemProduct', ''), key=f"{item_key_prefix}_prod")
                    if new_prod != data_item.get('itemProduct', ''): data_item['itemProduct'] = new_prod; st.rerun()

                    store_options_map = {k: v[list(v.keys())[0]]['name'].split('(')[0].strip() or k.replace('_', ' ') for k, v in INITIAL_BASE_CAPTIONS.items()}
                    current_store_key = data_item.get('selectedStoreKey', st.session_state.global_selected_store_key)
                    if current_store_key not in store_options_map:
                        current_store_key = list(store_options_map.keys())[0] if store_options_map else None
                        data_item['selectedStoreKey'] = current_store_key 

                    try:
                        store_idx = list(store_options_map.keys()).index(current_store_key) if current_store_key else 0
                    except ValueError: store_idx = 0
                    
                    selected_store_display_name = st.selectbox("Store", options=list(store_options_map.values()), index=store_idx, key=f"{item_key_prefix}_store")
                    new_selected_store_key = next((k for k, v_disp in store_options_map.items() if v_disp == selected_store_display_name), current_store_key) 
                    if new_selected_store_key != data_item.get('selectedStoreKey'): data_item['selectedStoreKey'] = new_selected_store_key; st.rerun()
                    
                    price_fmt_map = {p['value']: p['label'] for p in PREDEFINED_PRICES}
                    current_price_format = data_item.get('selectedPriceFormat', PREDEFINED_PRICES[1]['value'])
                    try: p_fmt_idx = list(price_fmt_map.keys()).index(current_price_format)
                    except ValueError: p_fmt_idx = 1 
                    
                    selected_price_format_val = st.selectbox("Price Format", options=list(price_fmt_map.keys()), format_func=lambda x: price_fmt_map[x], index=p_fmt_idx, key=f"{item_key_prefix}_pfmt")
                    if selected_price_format_val != data_item.get('selectedPriceFormat'): data_item['selectedPriceFormat'] = selected_price_format_val; st.rerun()

                    if selected_price_format_val == "CUSTOM":
                        new_custom_p = st.text_input("Custom Price Text", value=data_item.get('customItemPrice', ''), key=f"{item_key_prefix}_pcustom")
                        if new_custom_p != data_item.get('customItemPrice', ''): data_item['customItemPrice'] = new_custom_p; st.rerun()
                    elif selected_price_format_val == "X for $Y":
                        new_xfory_p = st.text_input("Price (e.g., 2 for $5.00)", value=data_item.get('itemPriceValue', ''), key=f"{item_key_prefix}_pxfory")
                        if new_xfory_p != data_item.get('itemPriceValue', ''): data_item['itemPriceValue'] = new_xfory_p; st.rerun()
                    else:
                        new_pval = st.text_input("Price Value (e.g., 1.99 or 79)", value=data_item.get('itemPriceValue', ''), key=f"{item_key_prefix}_pval")
                        if new_pval != data_item.get('itemPriceValue', ''): data_item['itemPriceValue'] = new_pval; st.rerun()

                    date_c1, date_c2 = st.columns(2)
                    with date_c1:
                        try: s_dt_val = datetime.datetime.strptime(data_item['dateRange']['start'], "%Y-%m-%d").date()
                        except: s_dt_val = datetime.date.today()
                        new_s_dt = st.date_input("Start Date", value=s_dt_val, key=f"{item_key_prefix}_sdate")
                        if new_s_dt.strftime("%Y-%m-%d") != data_item['dateRange']['start']: data_item['dateRange']['start'] = new_s_dt.strftime("%Y-%m-%d"); st.rerun()
                    with date_c2:
                        try: e_dt_val = datetime.datetime.strptime(data_item['dateRange']['end'], "%Y-%m-%d").date()
                        except: e_dt_val = datetime.date.today() + datetime.timedelta(days=6)
                        # Ensure min_value for end_date is correctly set based on new_s_dt
                        current_start_date_for_end_picker = datetime.datetime.strptime(data_item['dateRange']['start'], "%Y-%m-%d").date()
                        new_e_dt = st.date_input("End Date", value=e_dt_val, key=f"{item_key_prefix}_edate", min_value=current_start_date_for_end_picker)
                        if new_e_dt.strftime("%Y-%m-%d") != data_item['dateRange']['end']: data_item['dateRange']['end'] = new_e_dt.strftime("%Y-%m-%d"); st.rerun()
                
                caption_loading_key = f"{item_key_prefix}_caption_loading"
                if caption_loading_key not in st.session_state: st.session_state[caption_loading_key] = False

                if st.button(f"✍️ Generate Caption for {data_item.get('original_filename', 'this item')}", key=f"{item_key_prefix}_gen_btn", disabled=st.session_state[caption_loading_key], type="primary", use_container_width=True):
                    st.session_state[caption_loading_key] = True
                    data_item['generatedCaption'] = "" 
                    
                    store_details_key = data_item['selectedStoreKey']
                    store_info_set = INITIAL_BASE_CAPTIONS.get(store_details_key)
                    current_error = ""

                    if not store_info_set: current_error += f"Store details for '{store_details_key}' not found. "
                    else:
                        sale_detail_sub_key = list(store_info_set.keys())[0] 
                        if store_details_key == 'TEDS_FRESH_MARKET':
                            day_for_teds = get_current_day_for_teds() 
                            if day_for_teds == 2: sale_detail_sub_key = 'THREE_DAY'
                            elif day_for_teds == 5: sale_detail_sub_key = 'FOUR_DAY'
                        
                        caption_structure = store_info_set.get(sale_detail_sub_key)
                        if not caption_structure: current_error += f"Caption structure for '{sale_detail_sub_key}' under '{store_details_key}' not found. "
                        else:
                            final_price = get_final_price_string(data_item['selectedPriceFormat'], data_item['itemPriceValue'], data_item['customItemPrice'])
                            if not data_item.get('itemProduct', '').strip():
                                current_error += "Product name is missing. "
                            if not final_price or "[Price Value]" in final_price or "[Custom Price]" in final_price or "[X for $Y Price]" in final_price:
                                current_error += "Invalid or missing price. "
                            
                            display_dates = format_dates_for_caption_context(
                                data_item['dateRange']['start'], data_item['dateRange']['end'],
                                caption_structure['dateFormat'], caption_structure['language']
                            )
                            if "MISSING" in display_dates or "INVALID" in display_dates:
                                current_error += "Invalid date range for caption. "

                            if not current_error: 
                                holiday_ctx = get_holiday_context(data_item['dateRange']['start'], data_item['dateRange']['end'])
                                prompt_list = [
                                    f"Generate a social media caption for a grocery store promotion.",
                                    f"Store & Sale Type: {caption_structure['name']}",
                                    f"Product on Sale: {data_item['itemProduct']}", f"Price: {final_price}",
                                    f"Sale Dates (for display in caption): {display_dates}. (The actual sale period is from {data_item['dateRange']['start']} to {data_item['dateRange']['end']})."
                                ]
                                if holiday_ctx: prompt_list.append(f"Relevant Holiday Context: {holiday_ctx}.")
                                prompt_list.extend([
                                    f"Store Location: {caption_structure['location']}.",
                                    f"Language for caption: {caption_structure['language']}.",
                                    f"Desired Tone: {st.session_state.global_selected_tone}."
                                ])
                                if holiday_ctx and st.session_state.global_selected_tone == "Seasonal / Festive":
                                    prompt_list.append(f"Strongly emphasize the {holiday_ctx} theme and use relevant emojis.")
                                
                                prompt_list.extend([
                                    f"\nReference Style (from original example - adapt, don't copy verbatim):\n\"{caption_structure['original_example']}\"",
                                    "\nCaption Requirements:",
                                    "- The caption must be unique, engaging, and ready for social media.",
                                    "- Clearly include the product name, its price, the sale dates (as per 'display_dates'), and the store location.",
                                    f"- Incorporate relevant emojis suitable for the product, tone, and any holiday context ({holiday_ctx or 'general appeal'}).",
                                    f"- Include these base hashtags: {caption_structure['baseHashtags']}. Add 2-3 creative, relevant hashtags (product-specific, seasonal if applicable).",
                                    f"- The store's main name ({caption_structure['name'].split('(')[0].strip()}) should be prominent if the location \"{caption_structure['location']}\" is just a city/area.",
                                    "- Ensure good formatting with line breaks for readability on social media platforms."
                                ])
                                if caption_structure.get('durationTextPattern'):
                                    prompt_list.append(f"- Naturally integrate the promotional phrase \"{caption_structure['durationTextPattern']}\" with the sale dates {display_dates} if it makes sense (e.g., '3 DAYS ONLY {display_dates}').")
                                
                                final_prompt_for_caption = "\n".join(prompt_list)
                                try:
                                    generated_text = generate_caption_with_gemini(TEXT_MODEL, final_prompt_for_caption)
                                    data_item['generatedCaption'] = generated_text
                                except Exception as e: current_error += f"Caption API error: {str(e)}"
                    
                    data_item['analysisError'] = (data_item.get('analysisError', "").strip() + " " + current_error.strip()).strip()
                    st.session_state[caption_loading_key] = False
                    st.rerun()

                if st.session_state[caption_loading_key]:
                    st.caption("⏳ Generating caption...")

                if data_item.get('generatedCaption'):
                    st.text_area("📝 Generated Caption:", value=data_item['generatedCaption'], height=250, key=f"{item_key_prefix}_capt_out", help="Review and manually copy the text. Edit if needed.")
            st.markdown("---") 
    else:
        if not st.session_state.is_analyzing_images and not st.session_state.uploaded_files_info:
            st.info("☝️ Upload some images of grocery sale ads to get started!")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Caption Gen v3.2 // {datetime.date.today().strftime('%Y-%m-%d')}") # Incremented version

if __name__ == "__main__":
    main()
