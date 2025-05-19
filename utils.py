# utils.py
import datetime
from dateutil.parser import parse as dateutil_parse
# from dateutil.relativedelta import relativedelta # Not used in the provided helper functions
import re

def get_current_day_for_teds():
    py_weekday = datetime.date.today().weekday() # Monday is 0 and Sunday is 6
    # Convert to a system where Sunday=0, Monday=1, ..., Saturday=6 if that was the original JS logic.
    # The provided Python logic seems to directly map Python's weekday():
    # Tuesday (1 in Python) -> 2 in some logic. Friday (4 in Python) -> 5 in some logic.
    # Let's assume the direct use of Python's weekday or a known mapping is intended.
    # Based on original code: if js_equivalent_day == 2 (Tuesday), if js_equivalent_day == 5 (Friday)
    # Python's weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    # So, Tuesday is py_weekday == 1. Friday is py_weekday == 4.
    if py_weekday == 1: return 2 # Tuesday mapping
    if py_weekday == 4: return 5 # Friday mapping
    # Fallback:
    # The original JS conversion was: js_equivalent_day = (py_weekday + 1) % 7
    # Mon (0) -> (0+1)%7 = 1
    # Tue (1) -> (1+1)%7 = 2
    # Fri (4) -> (4+1)%7 = 5
    # Sun (6) -> (6+1)%7 = 0
    # This mapping is consistent with the checks for 2 and 5.
    return (py_weekday + 1) % 7


def get_nth_day_of_week(year, month, week_num, day_of_week_py): # Mon=0..Sun=6
    first_day_of_month = datetime.date(year, month, 1)
    days_to_add = (day_of_week_py - first_day_of_month.weekday() + 7) % 7
    nth_day = first_day_of_month + datetime.timedelta(days=days_to_add + (week_num - 1) * 7)
    if nth_day.month == month:
        return nth_day
    return None

def get_last_day_of_week(year, month, day_of_week_py): # Mon=0..Sun=6
    if month == 12:
        last_day_of_month = datetime.date(year, month, 31)
    else:
        last_day_of_month = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    days_to_subtract = (last_day_of_month.weekday() - day_of_week_py + 7) % 7
    return last_day_of_month - datetime.timedelta(days=days_to_subtract)

def get_holiday_context(start_date_str, end_date_str):
    if not start_date_str or not end_date_str: return ""
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError: return ""

    holidays = [
        {'name': "New Year's Day", 'type': 'fixed', 'month': 1, 'day': 1},
        {'name': "Martin Luther King Jr. Day", 'type': 'nthDayOfWeek', 'month': 1, 'week': 3, 'dayOfWeek': 0}, # Monday
        {'name': "Valentine's Day", 'type': 'fixed', 'month': 2, 'day': 14},
        {'name': "Presidents' Day", 'type': 'nthDayOfWeek', 'month': 2, 'week': 3, 'dayOfWeek': 0}, # Monday
        {'name': "St. Patrick's Day", 'type': 'fixed', 'month': 3, 'day': 17},
        # Simplified Easter to a month range, as exact calculation is complex and region-dependent.
        {'name': "Easter Season", 'type': 'monthRange', 'startMonth': 3, 'endMonth': 4},
        {'name': "Memorial Day", 'type': 'lastDayOfWeek', 'month': 5, 'dayOfWeek': 0}, # Last Monday
        {'name': "Juneteenth", 'type': 'fixed', 'month': 6, 'day': 19},
        {'name': "Independence Day (4th of July)", 'type': 'fixed', 'month': 7, 'day': 4},
        {'name': "Labor Day", 'type': 'nthDayOfWeek', 'month': 9, 'week': 1, 'dayOfWeek': 0}, # First Monday
        {'name': "Indigenous Peoples' Day/Columbus Day", 'type': 'nthDayOfWeek', 'month': 10, 'week': 2, 'dayOfWeek': 0}, # Second Monday
        {'name': "Halloween", 'type': 'fixed', 'month': 10, 'day': 31},
        {'name': "Veterans Day", 'type': 'fixed', 'month': 11, 'day': 11},
        {'name': "Thanksgiving Day", 'type': 'nthDayOfWeek', 'month': 11, 'week': 4, 'dayOfWeek': 3}, # 4th Thursday
        {'name': "Christmas Day", 'type': 'fixed', 'month': 12, 'day': 25}
    ]
    current_d = start_date
    while current_d <= end_date:
        cY, cM, cDOM = current_d.year, current_d.month, current_d.day
        for h in holidays:
            if h['type'] == 'fixed' and h['month'] == cM and h['day'] == cDOM: return h['name']
            elif h['type'] == 'nthDayOfWeek':
                hd = get_nth_day_of_week(cY, h['month'], h['week'], h['dayOfWeek'])
                if hd and hd == current_d: return h['name']
            elif h['type'] == 'lastDayOfWeek':
                hd = get_last_day_of_week(cY, h['month'], h['dayOfWeek'])
                if hd and hd == current_d: return h['name']
            elif h['type'] == 'monthRange' and h['startMonth'] <= cM <= h['endMonth']:
                 # For month range, ensure the range is significant to the holiday.
                 # E.g., if Easter is in late March, a sale early March might not be "Easter Season"
                 # This simple check is okay for general context.
                return h['name']
        current_d += datetime.timedelta(days=1)
    return ""

def format_date_string_for_caption_display(date_obj, lang="english", is_hasta_format=False, include_year=False):
    if not date_obj: return ''
    day = f"{date_obj.day:02d}"
    month = f"{date_obj.month:02d}"
    year_suffix = ""
    if include_year:
        year_suffix = f"/{date_obj.year % 100:02d}"

    if is_hasta_format: # Spanish DD/MM, English MM/DD
        base = f"{day}/{month}" if lang == "spanish" else f"{month}/{day}"
        return base + year_suffix
    # Default format MM/DD or DD/MM based on lang for ranges
    if lang == "spanish":
        return f"{day}/{month}" + year_suffix
    return f"{month}/{day}" + year_suffix


def format_dates_for_caption_context(start_str, end_str, date_format_pattern, lang):
    if not start_str or not end_str: return "DATES_MISSING"
    try:
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError: return "INVALID_DATES"

    is_hasta = date_format_pattern.lower().startswith("hasta")
    # Check if year is explicitly needed, e.g. "Hasta DD/MM/YY"
    include_year = "yy" in date_format_pattern.lower() or "yyyy" in date_format_pattern.lower()


    if is_hasta:
        # For "Hasta" formats, only the end date is typically shown.
        # Year inclusion depends on its presence in the original pattern.
        return format_date_string_for_caption_display(end_date, lang, is_hasta_format=True, include_year=include_year)

    # For ranges like MM/DD-MM/DD or MM/DD - MM/DD
    # Year inclusion for ranges is less common unless spanning years or explicitly in pattern.
    # We'll assume year is not included for ranges unless 'yy' is in the pattern.
    start_formatted = format_date_string_for_caption_display(start_date, lang, is_hasta_format=False, include_year=include_year)
    end_formatted = format_date_string_for_caption_display(end_date, lang, is_hasta_format=False, include_year=include_year)
    
    separator = " - " if ' - ' in date_format_pattern else "-"
    return f"{start_formatted}{separator}{end_formatted}"


def get_final_price_string(price_format, price_value, custom_val):
    if price_format == "CUSTOM": return custom_val if custom_val else "[Custom Price]"
    if price_format == "X for $Y": return price_value if price_value else "[X for $Y Price]"
    if not price_value: return f"[Price Value] {price_format.split(' ',1)[1] if ' ' in price_format else ''}"
    
    price_value_str = str(price_value)

    if price_format == "¢ / lb.": return f"{price_value_str}¢ / lb."
    if price_format == "$ / lb.": return f"${price_value_str} / lb."
    if price_format == "$ each": return f"${price_value_str} each"
    if price_format == "¢ each": return f"{price_value_str}¢ each"
    return price_value_str # Should not be reached if format is one of the above

def find_store_key_by_name(name_from_image, base_captions_data):
    if not name_from_image: return None
    norm_name = re.sub(r'[^A-Z0-9]', '', name_from_image.upper())
    for key, variants in base_captions_data.items():
        # Get the base name from the first variant of the store
        first_variant_key = list(variants.keys())[0]
        store_name_raw = variants[first_variant_key]['name'].split('(')[0].strip()
        norm_store_name = re.sub(r'[^A-Z0-9]', '', store_name_raw.upper())
        if norm_store_name in norm_name or norm_name in norm_store_name:
            # Added check for empty norm_store_name to prevent false positives if name is empty
            if norm_store_name:
                return key
    return None

def try_parse_date_from_image_text(text_from_image):
    if not text_from_image or not isinstance(text_from_image, str): return None
    text_from_image = text_from_image.strip()
    current_year = datetime.date.today().year
    
    cleaned_text = text_from_image.replace('.', '/') # . to /
    # Remove common non-date words. Careful with 'to' if it's part of a month name (though unlikely with MM/DD format)
    cleaned_text = re.sub(r'(?i)\b(ends|until|from|sale|starts|on|due|valido|expira|thru|through)\b\s*', '', cleaned_text).strip()
    cleaned_text = cleaned_text.replace(' ', '') # Remove spaces after keyword removal

    try:
        # Default to current year if no year is parsed.
        # Try dayfirst=False (MM/DD) common in US, then dayfirst=True (DD/MM) if needed.
        # Considering the prompt asks for MM/DD, dayfirst=False should be prioritized.
        dt_obj = dateutil_parse(cleaned_text, dayfirst=False, default=datetime.datetime(current_year, 1, 1))
        
        original_had_year = re.search(r'\b(19\d{2}|20\d{2})\b', text_from_image)
        original_had_short_year = re.search(r'\b(\d{1,2}/\d{1,2}/)(\d{2})\b', text_from_image)


        # If dateutil_parse defaulted to Jan 1st because only day/month was found,
        # and the original string did not suggest a year, set to current year if it's not already.
        if not original_had_year and not original_had_short_year and dt_obj.year != current_year:
            dt_obj = dt_obj.replace(year=current_year)
        # If original had a year but dateutil picked a year far from current, or defaulted to 1
        elif original_had_year and (abs(dt_obj.year - current_year) > 5 or dt_obj.year == 1):
             # Try re-parsing with fuzzy matching for complex strings if dateutil made a wild guess.
            try:
                dt_obj_fuzzy = dateutil_parse(cleaned_text, dayfirst=False, fuzzy=True, default=datetime.datetime(current_year, 1, 1))
                if abs(dt_obj_fuzzy.year - current_year) <= 5 : # More reasonable year
                    dt_obj = dt_obj_fuzzy
                else: # Fuzzy didn't help, or still bad year
                    return None
            except: # Fuzzy parsing failed
                 return None # Original parse was too ambiguous with a year
        
        # If only MM/DD was present and parsed, and year became default (e.g. 1/1), ensure current year.
        if dt_obj.year == 1 and not original_had_year and not original_had_short_year:
             dt_obj = dt_obj.replace(year=current_year)


        # Final check on year validity
        if not (current_year - 2 <= dt_obj.year <= current_year + 5): # Allow a small window for past/future sales
            # If year seems off and wasn't explicitly in text, try with current year
            if not original_had_year and not original_had_short_year:
                dt_obj = dt_obj.replace(year=current_year)
            # else if original had a year and it's still this far off, it's likely a misparse
            elif original_had_year and not (current_year - 2 <= dt_obj.year <= current_year + 5) :
                 return None


        return dt_obj.strftime("%Y-%m-%d")
        
    except (ValueError, TypeError, OverflowError):
        # Fallback to regex for M/D or M/D/YY or M/D/YYYY if dateutil fails
        # These patterns are for MM/DD format as primary
        patterns = [
            r"(\d{1,2})/(\d{1,2})/(\d{4})", # MM/DD/YYYY or M/D/YYYY
            r"(\d{1,2})/(\d{1,2})/(\d{2})",  # MM/DD/YY or M/D/YY
            r"(\d{1,2})/(\d{1,2})"           # MM/DD or M/D
        ]
        for pattern in patterns:
            match = re.match(pattern, cleaned_text) # Match from start of cleaned_text
            if match:
                parts = [int(p) for p in match.groups()]
                try:
                    if len(parts) == 3:
                        m, d, y_part = parts[0], parts[1], parts[2]
                        y = y_part if y_part > 1000 else (2000 + y_part if y_part < 70 else 1900 + y_part) # Handle 2-digit year
                        # Validate month and day
                        if not (1 <= m <= 12 and 1 <= d <= 31): continue
                        return datetime.date(y, m, d).strftime("%Y-%m-%d")
                    elif len(parts) == 2:
                        m, d = parts[0], parts[1]
                        if not (1 <= m <= 12 and 1 <= d <= 31): continue
                        return datetime.date(current_year, m, d).strftime("%Y-%m-%d")
                except ValueError: continue # Invalid date (e.g., Feb 30)
    return None